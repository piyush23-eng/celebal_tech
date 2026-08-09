"""
Part 2: Data Cleaning
---------------------
Reads the raw CSVs, cleans them, and writes:
    data/cleaned/customers.csv
    data/cleaned/products.csv
    data/cleaned/orders.csv
    data/cleaned/order_items.csv
    reports/data_quality_report.md   <- every issue found, with counts

Cleaning is deliberately non-destructive: rows with issues are FIXED where
possible (date formats, product name casing) and FLAGGED where a fix would
be guessing (missing customer_id, invalid email, orphan order_items) rather
than silently dropped, so nothing disappears without a trace.
"""

import os
import re
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR = os.path.join(BASE, "data", "raw")
CLEAN_DIR = os.path.join(BASE, "data", "cleaned")
REPORT_DIR = os.path.join(BASE, "reports")
os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Fixes:
      - order_date: accepts 'YYYY-MM-DD HH:MM:SS' or 'DD-MM-YYYY HH:MM:SS'
        and normalises everything to 'YYYY-MM-DD HH:MM:SS'.
      - customer_id: blank / 'NULL' string -> real NaN, then flagged
        (not dropped -- these are still valid orders, just missing the FK).
    """
    df = df.copy()
    issues = {"wrong_date_format_fixed": 0, "unparseable_dates": 0, "missing_customer_id": 0}

    def parse_date(value):
        value = str(value).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S"):
            try:
                parsed = pd.to_datetime(value, format=fmt)
                if fmt == "%d-%m-%Y %H:%M:%S":
                    issues["wrong_date_format_fixed"] += 1
                return parsed
            except ValueError:
                continue
        issues["unparseable_dates"] += 1
        return pd.NaT

    df["order_date"] = df["order_date"].apply(parse_date)

    df["customer_id"] = df["customer_id"].replace(
        {"": pd.NA, "NULL": pd.NA, "null": pd.NA, "NaN": pd.NA}
    )
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    issues["missing_customer_id"] = int(df["customer_id"].isna().sum())
    df["customer_id_missing"] = df["customer_id"].isna()

    return df, issues


def clean_products(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Trims whitespace and applies title case to product_name."""
    df = df.copy()
    before = df["product_name"].copy()
    df["product_name"] = df["product_name"].str.strip().str.title()
    changed = int((before != df["product_name"]).sum())
    return df, {"product_names_normalized": changed}


def validate_emails(df: pd.DataFrame) -> list:
    """Returns customer_ids whose email is missing '@' or a domain."""
    bad = df.loc[~df["email"].str.match(EMAIL_RE, na=True), "customer_id"]
    return bad.tolist()


def check_referential_integrity(orders_df: pd.DataFrame, order_items_df: pd.DataFrame) -> pd.DataFrame:
    """Returns order_items rows whose order_id has no matching row in orders."""
    valid_ids = set(pd.to_numeric(orders_df["order_id"], errors="coerce").dropna().astype(int))
    order_ids_numeric = pd.to_numeric(order_items_df["order_id"], errors="coerce")
    orphans = order_items_df[~order_ids_numeric.isin(valid_ids)]
    return orphans


def clean_order_items(df: pd.DataFrame, orphan_ids: set) -> tuple[pd.DataFrame, dict]:
    """
    Flags (does not delete) the two documented anomaly types:
      - negative quantity -> returns, kept, tagged is_return
      - discount_percent outside [0, 100] -> tagged invalid_discount
    Orphan rows (bad order_id) ARE removed here since they cannot be
    attributed to any order and would break every downstream join.
    """
    df = df.copy()
    issues = {}
    issues["orphan_rows_removed"] = int(df["item_id"].isin(orphan_ids).sum()) if orphan_ids else 0
    if orphan_ids:
        df = df[~df["item_id"].isin(orphan_ids)]

    df["is_return"] = df["quantity"] < 0
    issues["negative_quantity_flagged"] = int(df["is_return"].sum())

    df["invalid_discount"] = ~df["discount_percent"].between(0, 100)
    issues["invalid_discount_flagged"] = int(df["invalid_discount"].sum())

    return df, issues


def main():
    customers = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"), dtype=str)
    products = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
    orders_raw = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"), dtype=str)
    order_items_raw = pd.read_csv(os.path.join(RAW_DIR, "order_items.csv"))

    orders_clean, order_issues = clean_orders(orders_raw)
    products_clean, product_issues = clean_products(products)
    bad_customer_ids = validate_emails(customers)

    orphans = check_referential_integrity(orders_clean, order_items_raw)
    order_items_clean, item_issues = clean_order_items(order_items_raw, set(orphans["item_id"]))

    customers.to_csv(os.path.join(CLEAN_DIR, "customers.csv"), index=False)
    products_clean.to_csv(os.path.join(CLEAN_DIR, "products.csv"), index=False)
    orders_clean.to_csv(os.path.join(CLEAN_DIR, "orders.csv"), index=False)
    order_items_clean.to_csv(os.path.join(CLEAN_DIR, "order_items.csv"), index=False)

    report_path = os.path.join(REPORT_DIR, "data_quality_report.md")
    with open(report_path, "w") as f:
        f.write("# Data Quality Report\n\n")
        f.write("## orders.csv\n")
        for k, v in order_issues.items():
            f.write(f"- **{k}**: {v}\n")
        f.write("\n## products.csv\n")
        for k, v in product_issues.items():
            f.write(f"- **{k}**: {v}\n")
        f.write("\n## customers.csv\n")
        f.write(f"- **invalid_emails**: {len(bad_customer_ids)}\n")
        f.write(f"- **affected customer_ids (first 20)**: {bad_customer_ids[:20]}\n")
        f.write("\n## order_items.csv\n")
        f.write(f"- **orphan_order_items_found**: {len(orphans)} (order_id not present in orders.csv)\n")
        for k, v in item_issues.items():
            f.write(f"- **{k}**: {v}\n")
        f.write(f"\n_Orphan item_ids removed: {sorted(orphans['item_id'].tolist())}_\n")

    print("Cleaning complete.")
    print(f"  Cleaned CSVs -> {os.path.abspath(CLEAN_DIR)}")
    print(f"  Report       -> {os.path.abspath(report_path)}")
    print(f"  Orphan order_items found & removed: {len(orphans)}")
    print(f"  Invalid emails found: {len(bad_customer_ids)}")


if __name__ == "__main__":
    main()
