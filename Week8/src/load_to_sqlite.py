"""Loads cleaned CSVs into a local SQLite database (data/ecommerce.db)."""

import os
import sqlite3
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..")
CLEAN_DIR = os.path.join(BASE, "data", "cleaned")
DB_PATH = os.path.join(BASE, "data", "ecommerce.db")


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)

    customers = pd.read_csv(os.path.join(CLEAN_DIR, "customers.csv"))
    products = pd.read_csv(os.path.join(CLEAN_DIR, "products.csv"))
    orders = pd.read_csv(os.path.join(CLEAN_DIR, "orders.csv"))
    order_items = pd.read_csv(os.path.join(CLEAN_DIR, "order_items.csv"))

    # order_id/customer_id come out of pandas as floats when NaNs are present;
    # normalise types before writing so joins behave inside SQLite.
    orders["order_id"] = orders["order_id"].astype(int)
    orders["customer_id"] = pd.to_numeric(orders["customer_id"], errors="coerce")
    order_items["order_id"] = order_items["order_id"].astype(int)
    order_items["product_id"] = order_items["product_id"].astype(int)
    products["product_id"] = products["product_id"].astype(int)
    customers["customer_id"] = customers["customer_id"].astype(int)

    customers.to_sql("customers", conn, if_exists="replace", index=False)
    products.to_sql("products", conn, if_exists="replace", index=False)
    orders.to_sql("orders", conn, if_exists="replace", index=False)
    order_items.to_sql("order_items", conn, if_exists="replace", index=False)

    cur = conn.cursor()
    for stmt in [
        "CREATE INDEX idx_orders_customer ON orders(customer_id)",
        "CREATE INDEX idx_orders_date ON orders(order_date)",
        "CREATE INDEX idx_items_order ON order_items(order_id)",
        "CREATE INDEX idx_items_product ON order_items(product_id)",
    ]:
        cur.execute(stmt)
    conn.commit()

    counts = {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ["customers", "products", "orders", "order_items"]
    }
    print(f"SQLite DB written to {os.path.abspath(DB_PATH)}")
    for t, c in counts.items():
        print(f"  {t}: {c} rows")

    conn.close()


if __name__ == "__main__":
    main()
