"""
gold_layer.py
-------------
GOLD LAYER = business-ready analytics -- hardened.

Everything here consumes ONLY the sanitized Silver dataset. No raw
identifier ever reaches this layer -- analysts work exclusively with
customer_name_token (a stable but irreversible surrogate), age_band,
and spend_category.
"""

import logging
import os

import matplotlib
matplotlib.use("Agg")  # headless-safe: never assumes a display is available
import matplotlib.pyplot as plt
import pandas as pd

from exceptions import SchemaValidationError, SourceFileError

plt.rcParams["axes.unicode_minus"] = False
logger = logging.getLogger("lakehouse.gold")

REQUIRED_SILVER_COLUMNS = ["customer_name_token", "transaction_amount", "spend_category"]
SPEND_ORDER = ["Low (<1000)", "Medium (1000-5000)", "High (>5000)"]


def _fmt_rupee(x, _pos=None):
    return f"\u20b9{x:,.0f}"


def load_silver(silver_path: str) -> pd.DataFrame:
    if not os.path.exists(silver_path):
        raise SourceFileError(f"Silver file not found: '{silver_path}'. Run silver_layer.transform() first.")
    df = pd.read_csv(silver_path)
    if df.empty:
        raise SourceFileError(f"Silver file '{silver_path}' contains 0 rows -- nothing to aggregate.")
    missing = [c for c in REQUIRED_SILVER_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaValidationError(
            f"Gold layer requires columns {REQUIRED_SILVER_COLUMNS} but Silver output "
            f"is missing: {missing}. Check silver_layer.py hasn't dropped something it shouldn't."
        )
    return df


def total_vs_avg_by_category(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("spend_category")["transaction_amount"].agg(["sum", "mean"])
    g = g.rename(columns={"sum": "total_amount", "mean": "avg_amount"})
    # reindex to a fixed category order; categories with zero rows in
    # this batch show as 0 rather than silently vanishing from the chart
    g = g.reindex(SPEND_ORDER).fillna(0)
    return g


def spend_per_customer(df: pd.DataFrame) -> pd.Series:
    g = df.groupby("customer_name_token")["transaction_amount"].sum()
    return g.sort_values(ascending=False)


def transaction_distribution(df: pd.DataFrame) -> pd.Series:
    counts = df["spend_category"].value_counts()
    return counts.reindex(SPEND_ORDER).fillna(0).astype(int)


def chart_total_vs_avg(summary: pd.DataFrame, outpath: str):
    fig, ax = plt.subplots(figsize=(7, 5))
    x = range(len(summary))
    width = 0.35
    b1 = ax.bar([i - width / 2 for i in x], summary["total_amount"], width, label="Total Amount", color="#3399ff")
    b2 = ax.bar([i + width / 2 for i in x], summary["avg_amount"], width, label="Avg Amount", color="#ff9900")
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary.index, rotation=0)
    ax.set_ylabel("Amount (\u20b9)")
    ax.set_title("Total vs Avg Amount by Spend Category", fontweight="bold")
    ax.legend()
    for bars, color in [(b1, "#1a5fb4"), (b2, "#cc6600")]:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(_fmt_rupee(h), (bar.get_x() + bar.get_width() / 2, h),
                        textcoords="offset points", xytext=(0, 4), ha="center",
                        fontsize=8, color=color, fontweight="bold")
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(_fmt_rupee))
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close(fig)


def chart_avg_spend_per_customer(customer_stats: pd.DataFrame, outpath: str):
    fig, ax = plt.subplots(figsize=(7, 8))
    ranked = customer_stats.sort_values("avg_amount", ascending=True)
    ax.barh(range(len(ranked)), ranked["avg_amount"], color="#2e7d32")
    ax.set_yticks([])
    ax.set_xlabel("Average Spend (\u20b9)")
    ax.set_title("Avg Spend per Customer (Ranked)", fontweight="bold")
    ax.get_xaxis().set_major_formatter(plt.FuncFormatter(_fmt_rupee))
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close(fig)


def chart_total_spend_per_customer(customer_totals_sorted: pd.Series, outpath: str):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(customer_totals_sorted)), customer_totals_sorted.values, color="#1a1a1a", width=0.8)
    ax.set_xticks([])
    ax.set_ylabel("Total Spend (\u20b9)")
    ax.set_title("Total Spend by Customer (Token-Anonymized)", fontweight="bold")
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(_fmt_rupee))
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close(fig)


def chart_transaction_distribution(counts: pd.Series, outpath: str):
    colors = ["#43a047", "#fb8c00", "#e91e63"]
    nonzero = counts[counts > 0]
    if nonzero.empty:
        logger.warning("No transactions in any spend category -- skipping pie chart.")
        return
    labels = [f"{cat}\n{cnt} txns" for cat, cnt in nonzero.items()]
    used_colors = [colors[SPEND_ORDER.index(cat)] for cat in nonzero.index]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        nonzero.values, labels=labels, colors=used_colors, autopct="%1.0f%%",
        startangle=90, explode=[0.03] * len(nonzero),
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 9},
    )
    ax.set_title("Transaction Distribution by Spend Category", fontweight="bold")
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close(fig)


def run(silver_path: str, gold_dir: str):
    df = load_silver(silver_path)

    summary = total_vs_avg_by_category(df)
    customer_totals = spend_per_customer(df)
    counts = transaction_distribution(df)
    customer_stats = df.groupby("customer_name_token")["transaction_amount"].agg(
        total_amount="sum", avg_amount="mean", txn_count="count"
    )

    os.makedirs(gold_dir, exist_ok=True)
    summary.to_csv(f"{gold_dir}/total_vs_avg_by_category.csv")
    customer_stats.to_csv(f"{gold_dir}/customer_spend_summary.csv")
    counts.to_csv(f"{gold_dir}/transaction_distribution.csv")

    chart_total_vs_avg(summary, f"{gold_dir}/chart_total_vs_avg_by_category.png")
    chart_avg_spend_per_customer(customer_stats, f"{gold_dir}/chart_avg_spend_per_customer.png")
    chart_total_spend_per_customer(
        customer_totals.sort_values(ascending=False), f"{gold_dir}/chart_total_spend_by_customer.png"
    )
    chart_transaction_distribution(counts, f"{gold_dir}/chart_transaction_distribution.png")

    logger.info("Business analytics complete.\n%s", summary)
    logger.info("Charts saved to %s", gold_dir)
    return summary, customer_stats, counts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    run("silver/silver_transactions.csv", "gold")
