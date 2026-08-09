"""
Executes every query in sql/analysis.sql against data/ecommerce.db,
saves each result set to query_results/NN_description.csv, and writes
query_results/SUMMARY.md with row counts + a preview of each result.
"""

import os
import re
import sqlite3
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE, "data", "ecommerce.db")
SQL_PATH = os.path.join(BASE, "sql", "analysis.sql")
OUT_DIR = os.path.join(BASE, "query_results")
os.makedirs(OUT_DIR, exist_ok=True)

QUERY_TITLES = {
    1: "total_revenue_per_category",
    2: "top_10_customers_by_value",
    3: "monthwise_order_count_last_12m",
    4: "customers_never_delivered",
    5: "products_more_returns_than_purchases",
    6: "return_rate_per_category",
    7: "running_total_revenue_per_region",
    8: "product_rank_by_revenue_dense_rank",
    9: "days_between_orders_lag",
    10: "cte_multilevel_revenue_category_counts",
    11: "ntile_customer_quartiles",
    12: "yoy_revenue_comparison",
    13: "first_last_category_shift",
    14: "cumulative_revenue_distribution",
    15: "cohort_retention",
    16: "products_frequently_bought_together",
}


def split_queries(sql_text: str) -> list:
    """Splits analysis.sql into individual runnable statements, numbered 1-16,
    based on the '-- N.' comment markers that precede each query."""
    # Drop the file header block before query 1
    parts = re.split(r"\n-- (\d+)\.\s", sql_text)
    # parts[0] is header/basic-queries banner text -> discard
    statements = {}
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        body = parts[i + 1]
        # first line after "-- N." is the plain-text title (e.g. "Total revenue per category")
        # drop it; everything after is either a comment or the actual statement
        first_newline = body.find("\n")
        body = body[first_newline + 1:]
        stmt_end = body.find(";")
        stmt = body[:stmt_end] if stmt_end != -1 else body
        statements[num] = stmt.strip()
    return statements


def main():
    with open(SQL_PATH) as f:
        sql_text = f.read()
    statements = split_queries(sql_text)

    conn = sqlite3.connect(DB_PATH)
    summary_lines = ["# Query Results Summary\n"]

    for num in sorted(statements):
        title = QUERY_TITLES.get(num, f"query_{num}")
        stmt = statements[num]
        try:
            df = pd.read_sql_query(stmt, conn)
            out_path = os.path.join(OUT_DIR, f"{num:02d}_{title}.csv")
            df.to_csv(out_path, index=False)
            summary_lines.append(f"## Query {num}: {title.replace('_', ' ')}")
            summary_lines.append(f"- rows returned: {len(df)}")
            summary_lines.append(f"- saved to: query_results/{num:02d}_{title}.csv")
            summary_lines.append("")
            summary_lines.append(df.head(5).to_markdown(index=False))
            summary_lines.append("")
            print(f"[OK]  Query {num:2d} ({title}) -> {len(df)} rows")
        except Exception as e:
            summary_lines.append(f"## Query {num}: {title.replace('_', ' ')}")
            summary_lines.append(f"- ERROR: {e}")
            summary_lines.append("")
            print(f"[FAIL] Query {num:2d} ({title}) -> {e}")

    with open(os.path.join(OUT_DIR, "SUMMARY.md"), "w") as f:
        f.write("\n".join(summary_lines))

    conn.close()
    print(f"\nAll results saved in {os.path.abspath(OUT_DIR)}")


if __name__ == "__main__":
    main()
