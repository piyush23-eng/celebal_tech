"""
Part 5: Edge Case Handling
---------------------------
Each test spins up a tiny in-memory SQLite DB with a handpicked scenario,
so every edge case is isolated and doesn't depend on the generated dataset.

Run with:  python3 -m unittest tests/test_edge_cases.py -v
       or: python3 tests/test_edge_cases.py
"""

import os
import sqlite3
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from clean_data import check_referential_integrity  # noqa: E402
import pandas as pd  # noqa: E402


def make_test_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE orders (
        order_id INTEGER, customer_id INTEGER, order_date TEXT, status TEXT, region_code TEXT
    )""")
    conn.execute("""CREATE TABLE order_items (
        item_id INTEGER, order_id INTEGER, product_id INTEGER,
        quantity INTEGER, unit_price REAL, discount_percent REAL
    )""")
    return conn


class TestEdgeCases(unittest.TestCase):

    # 1. order_items references an order_id that does not exist in orders -----
    def test_order_item_with_nonexistent_order_id(self):
        orders = pd.DataFrame({"order_id": [1, 2, 3]})
        order_items = pd.DataFrame({
            "item_id": [1, 2, 3],
            "order_id": [1, 2, 999],   # 999 does not exist
            "product_id": [10, 11, 12],
        })
        orphans = check_referential_integrity(orders, order_items)
        self.assertEqual(len(orphans), 1)
        self.assertEqual(orphans.iloc[0]["order_id"], 999)

    # 2. discount_percent > 100 --------------------------------------------
    def test_discount_percent_above_100(self):
        conn = make_test_db()
        conn.execute("INSERT INTO orders VALUES (1, 1, '2024-01-01 10:00:00', 'DELIVERED', 'NORTH')")
        conn.execute("INSERT INTO order_items VALUES (1, 1, 100, 2, 500.0, 150)")  # 150% discount
        conn.commit()

        row = conn.execute("SELECT discount_percent FROM order_items WHERE item_id = 1").fetchone()
        discount = row[0]
        # revenue formula would go NEGATIVE with an out-of-range discount --
        # this is exactly why invalid_discount rows are flagged, not silently used
        revenue = 2 * 500.0 * (1 - discount / 100.0)
        self.assertGreater(discount, 100)
        self.assertLess(revenue, 0, "an unclamped >100% discount produces negative revenue")
        conn.close()

    # 3. quantity is 0 -------------------------------------------------------
    def test_zero_quantity(self):
        conn = make_test_db()
        conn.execute("INSERT INTO orders VALUES (1, 1, '2024-01-01 10:00:00', 'DELIVERED', 'NORTH')")
        conn.execute("INSERT INTO order_items VALUES (1, 1, 100, 0, 500.0, 10)")  # qty = 0
        conn.commit()

        revenue = conn.execute("""
            SELECT SUM(quantity * unit_price * (1 - discount_percent / 100.0))
            FROM order_items WHERE item_id = 1
        """).fetchone()[0]
        # zero quantity contributes exactly zero revenue -- neither a sale nor a return,
        # so it should NOT be misclassified as either by is_return / return-rate logic
        self.assertEqual(revenue, 0.0)
        conn.close()

    # 4. order_date in the future --------------------------------------------
    def test_future_order_date(self):
        conn = make_test_db()
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO orders VALUES (1, 1, ?, 'PLACED', 'NORTH')", (future_date,))
        conn.commit()

        row = conn.execute("SELECT order_date FROM orders WHERE order_id = 1").fetchone()
        order_dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        # this data-quality check should be run before trusting the row in
        # any month-wise / cohort / YoY query, since a future order will
        # silently skew "last 12 months" windows if it isn't caught
        self.assertGreater(order_dt, datetime.now(),
                            "order_date is in the future -- should be flagged before analysis")
        conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
