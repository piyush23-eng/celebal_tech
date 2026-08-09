"""
Part 4: Python + SQL Integration
---------------------------------
A command-line report generator. Stdlib only (argparse, sqlite3, datetime) --
no pandas, no external packages, as required by the brief.

Usage examples
--------------
    python3 src/cli_report.py --type monthly --start 2024-01-01 --end 2024-01-31
    python3 src/cli_report.py --type weekly  --start 2024-06-01 --end 2024-06-07
    python3 src/cli_report.py --type daily   --start 2024-06-15 --end 2024-06-15
    python3 src/cli_report.py                       # interactive prompts
"""

import argparse
import os
import sqlite3
from datetime import datetime, timedelta

BASE = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE, "data", "ecommerce.db")

REVENUE_EXPR = "oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)"


def parse_args():
    parser = argparse.ArgumentParser(description="E-commerce order analytics report generator")
    parser.add_argument("--type", choices=["daily", "weekly", "monthly"], help="Report type")
    parser.add_argument("--start", help="Start date, YYYY-MM-DD")
    parser.add_argument("--end", help="End date, YYYY-MM-DD")
    return parser.parse_args()


def prompt_missing(args):
    if not args.type:
        args.type = input("Report type (daily/weekly/monthly): ").strip().lower()
    if not args.start:
        args.start = input("Start date (YYYY-MM-DD): ").strip()
    if not args.end:
        args.end = input("End date   (YYYY-MM-DD): ").strip()
    return args


def previous_period(start: str, end: str):
    """Same-length window immediately preceding the given range."""
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    length = (end_dt - start_dt) + timedelta(days=1)
    prev_end = start_dt - timedelta(days=1)
    prev_start = prev_end - length + timedelta(days=1)
    return prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")


def fetch_period_stats(conn, start: str, end: str) -> dict:
    cur = conn.cursor()

    cur.execute(f"""
        SELECT
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS unique_customers,
            COALESCE(SUM({REVENUE_EXPR}), 0) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE date(o.order_date) BETWEEN date(?) AND date(?)
    """, (start, end))
    total_orders, unique_customers, revenue = cur.fetchone()

    cur.execute(f"""
        SELECT p.product_name, SUM({REVENUE_EXPR}) AS product_revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        JOIN products p ON p.product_id = oi.product_id
        WHERE date(o.order_date) BETWEEN date(?) AND date(?)
        GROUP BY p.product_name
        ORDER BY product_revenue DESC
        LIMIT 3
    """, (start, end))
    top_products = cur.fetchall()

    return {
        "total_orders": total_orders or 0,
        "unique_customers": unique_customers or 0,
        "revenue": round(revenue or 0, 2),
        "top_products": top_products,
    }


def pct_change(new_val, old_val):
    if not old_val:
        return None
    return round(100.0 * (new_val - old_val) / old_val, 2)


def print_report(report_type, start, end, current, prev_start, prev_end, previous):
    bar = "=" * 60
    print(bar)
    print(f"  {report_type.upper()} REPORT   |   {start} to {end}")
    print(bar)
    print(f"  Total Orders       : {current['total_orders']}")
    print(f"  Total Revenue      : Rs {current['revenue']:,.2f}")
    print(f"  Unique Customers   : {current['unique_customers']}")
    print()
    print("  Top 3 Products:")
    if current["top_products"]:
        for i, (name, rev) in enumerate(current["top_products"], start=1):
            print(f"    {i}. {name:<35} Rs {rev:,.2f}")
    else:
        print("    (no order items in this period)")
    print()
    print(f"  vs. Previous Period ({prev_start} to {prev_end}):")
    o_pct = pct_change(current["total_orders"], previous["total_orders"])
    r_pct = pct_change(current["revenue"], previous["revenue"])
    c_pct = pct_change(current["unique_customers"], previous["unique_customers"])
    print(f"    Orders    : {previous['total_orders']:>6}  ->  {current['total_orders']:>6}   "
          f"({fmt_pct(o_pct)})")
    print(f"    Revenue   : Rs {previous['revenue']:>10,.2f}  ->  Rs {current['revenue']:>10,.2f}   "
          f"({fmt_pct(r_pct)})")
    print(f"    Customers : {previous['unique_customers']:>6}  ->  {current['unique_customers']:>6}   "
          f"({fmt_pct(c_pct)})")
    print(bar)


def fmt_pct(p):
    if p is None:
        return "n/a (no prior data)"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p}%"


def main():
    args = prompt_missing(parse_args())

    try:
        datetime.strptime(args.start, "%Y-%m-%d")
        datetime.strptime(args.end, "%Y-%m-%d")
    except ValueError:
        print("Error: dates must be in YYYY-MM-DD format.")
        return

    if not os.path.exists(DB_PATH):
        print(f"Error: database not found at {DB_PATH}. Run src/load_to_sqlite.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    current = fetch_period_stats(conn, args.start, args.end)
    prev_start, prev_end = previous_period(args.start, args.end)
    previous = fetch_period_stats(conn, prev_start, prev_end)
    conn.close()

    print_report(args.type, args.start, args.end, current, prev_start, prev_end, previous)


if __name__ == "__main__":
    main()
