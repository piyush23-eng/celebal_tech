"""
config.py
---------
Central configuration for the Secure Retail Data Lakehouse pipeline.

In a real production deployment, HASH_SALT would NEVER be hardcoded.
It would be pulled from a secrets manager (Azure Key Vault / AWS Secrets
Manager) via an environment variable, and rotated periodically.
For this project, we fall back to a local constant ONLY if the
environment variable is not set, purely so the pipeline is runnable
out-of-the-box for demonstration / review purposes.
"""

import os

# --- Security ---------------------------------------------------------
# Salt used for one-way SHA-256 tokenization of direct identifiers.
# Pulling from env var keeps the "real" secret out of source control.
HASH_SALT = os.environ.get("LAKEHOUSE_HASH_SALT", "demo-salt-do-not-use-in-prod")

# Columns that must be HARD-DROPPED the moment data lands in the lake.
# These are fields with zero downstream analytical value and maximum
# regulatory risk (PCI-DSS explicitly forbids storing CVV, period).
HARD_DROP_COLUMNS = ["cvv"]

# Columns that must be tokenized (irreversibly hashed) rather than
# just partially masked, because analysts need a *stable* surrogate
# key to join/group by, but must never see the real value.
TOKENIZE_COLUMNS = ["customer_name", "card_number"]

# Columns that get partial/format-preserving masking (human still needs
# to eyeball *something* for support/debugging without full exposure).
MASK_COLUMNS = ["email", "phone"]

# Age bands used to bin exact date_of_birth -> demographic bucket.
AGE_BINS = [0, 18, 25, 30, 40, 50, 60, 120]
AGE_LABELS = ["<18", "18-25", "25-30", "30-40", "40-50", "50-60", "60+"]

# Spend category thresholds (mirrors business definition supplied by
# the analytics team): Low <1000, Medium 1000-5000, High >5000.
SPEND_BINS = [0, 1000, 5000, float("inf")]
SPEND_LABELS = ["Low (<1000)", "Medium (1000-5000)", "High (>5000)"]


def _validate_bins():
    """Fail fast at import time if bins/labels are misconfigured, rather
    than producing silently wrong bucket assignments at runtime."""
    for name, bins, labels in [
        ("AGE", AGE_BINS, AGE_LABELS),
        ("SPEND", SPEND_BINS, SPEND_LABELS),
    ]:
        if len(bins) - 1 != len(labels):
            raise ValueError(
                f"{name}_BINS has {len(bins)} edges (=> {len(bins)-1} buckets) "
                f"but {name}_LABELS has {len(labels)} entries. These must match."
            )
        if list(bins) != sorted(bins):
            raise ValueError(f"{name}_BINS must be strictly ascending: got {bins}")


_validate_bins()

# Columns that, if ever found in a Silver or Gold output, indicate a
# serious pipeline bug -- checked defensively by silver_layer.py's
# leakage guard after every transform.
RAW_PII_COLUMNS = [
    "customer_name", "email", "phone", "address",
    "date_of_birth", "card_number", "cvv",
]

# Columns that must be present and non-null for a row to be considered
# safely processable. Rows failing this are quarantined, not dropped
# silently and not allowed to crash the whole batch.
REQUIRED_NON_NULL_COLUMNS = [
    "transaction_id", "customer_id", "transaction_amount", "transaction_date",
]

# Paths
RAW_PATH = "data/raw_transactions.csv"
BRONZE_PATH = "bronze/bronze_transactions.csv"
BRONZE_QUARANTINE_PATH = "bronze/quarantined_rows.csv"
SILVER_PATH = "silver/silver_transactions.csv"
GOLD_DIR = "gold"
