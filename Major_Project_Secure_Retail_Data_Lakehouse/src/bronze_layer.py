"""
bronze_layer.py
----------------
BRONZE LAYER = raw, as-is ingestion -- hardened.

Purpose: durable, immutable copy of exactly what the source system sent,
so we always have lineage back to the original extract. Nothing is
cleaned or masked here (that would defeat the point of Bronze) -- but
it IS validated, because a batch pipeline that crashes on one bad row
is not production-grade.

What Bronze is allowed to do:
  - hard-drop CVV immediately on arrival (see note below)
  - basic schema validation (right columns present)
  - quarantine (not silently drop, not crash on) rows that are
    structurally broken: missing required fields, non-numeric or
    negative transaction_amount, duplicate transaction_id
  - append ingestion metadata (ingested_at, source_system, batch_id)

Note on CVV specifically: the problem statement calls for CVV to be
"physically dropped immediately upon ingestion into the data lake" --
i.e. here, at Bronze, not one layer later at Silver. Every other
identifier (name, email, phone, card number, DOB, address) is retained
in Bronze as the immutable raw mirror and only masked/tokenized/binned
at Silver. CVV is the one field with zero legitimate use at any layer
-- PCI-DSS prohibits storing it at all -- so it is dropped here, at the
earliest possible point, instead of at Silver with everything else.

Access to this layer must be restricted to the platform/ingestion
service account only -- it still contains full PII + card-number data
(everything except CVV).
"""

import logging
import os
import uuid
from datetime import datetime, timezone

import pandas as pd

from config import BRONZE_QUARANTINE_PATH, REQUIRED_NON_NULL_COLUMNS
from exceptions import NoValidRowsError, SchemaValidationError, SourceFileError

logger = logging.getLogger("lakehouse.bronze")

EXPECTED_COLUMNS = [
    "transaction_id", "customer_id", "customer_name", "email", "phone",
    "address", "date_of_birth", "card_number", "cvv", "transaction_amount",
    "transaction_date", "store_channel",
]

HARD_DROP_ON_INGEST = ["cvv"]


def load_raw(raw_path: str) -> pd.DataFrame:
    """Load the raw source file, failing with a clear, specific error
    for the three most common real-world problems: missing file, empty
    file, and unparseable content -- instead of a raw pandas traceback."""
    if not os.path.exists(raw_path):
        raise SourceFileError(
            f"Raw source file not found: '{raw_path}'. "
            f"Run with --regen-data to generate a synthetic file, or "
            f"confirm the extract landed at this path."
        )
    if os.path.getsize(raw_path) == 0:
        raise SourceFileError(f"Raw source file '{raw_path}' is empty (0 bytes).")
    try:
        df = pd.read_csv(raw_path)
    except pd.errors.EmptyDataError as exc:
        raise SourceFileError(f"Raw source file '{raw_path}' has no parseable rows.") from exc
    except pd.errors.ParserError as exc:
        raise SourceFileError(f"Raw source file '{raw_path}' is malformed CSV: {exc}") from exc

    if df.empty:
        raise SourceFileError(f"Raw source file '{raw_path}' parsed successfully but contains 0 rows.")
    return df


def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaValidationError(
            f"Bronze ingestion failed schema check. Missing required columns: {missing}. "
            f"Expected columns: {EXPECTED_COLUMNS}"
        )
    return df


def _quarantine_mask(df: pd.DataFrame):
    """Row-level validity check. Returns (valid_mask, reason_masks dict).
    Anything False in valid_mask gets quarantined, not dropped silently
    and not allowed to crash the batch."""
    reasons_null = df[REQUIRED_NON_NULL_COLUMNS].isnull().any(axis=1)
    amount_numeric = pd.to_numeric(df["transaction_amount"], errors="coerce")
    reasons_bad_amount = amount_numeric.isnull() | (amount_numeric <= 0)
    reasons_bad_date = pd.to_datetime(df["transaction_date"], errors="coerce").isnull()
    reasons_dup_id = df.duplicated(subset=["transaction_id"], keep="first")

    is_bad = reasons_null | reasons_bad_amount | reasons_bad_date | reasons_dup_id
    reason_masks = {
        "null_required_field": reasons_null,
        "invalid_or_negative_amount": reasons_bad_amount,
        "unparseable_transaction_date": reasons_bad_date,
        "duplicate_transaction_id": reasons_dup_id,
    }
    return ~is_bad, reason_masks


def quarantine_bad_rows(df: pd.DataFrame, quarantine_path: str) -> pd.DataFrame:
    valid_mask, reason_masks = _quarantine_mask(df)
    bad_df = df[~valid_mask].copy()

    if not bad_df.empty:
        def _reasons_for_row(idx):
            return ",".join(name for name, mask in reason_masks.items() if mask.loc[idx])

        bad_df["_quarantine_reason"] = [_reasons_for_row(i) for i in bad_df.index]
        os.makedirs(os.path.dirname(quarantine_path) or ".", exist_ok=True)
        bad_df.to_csv(quarantine_path, index=False)
        logger.warning(
            "Quarantined %d/%d rows (%.1f%%) -> %s",
            len(bad_df), len(df), 100 * len(bad_df) / len(df), quarantine_path,
        )

    good_df = df[valid_mask].copy()
    if good_df.empty:
        raise NoValidRowsError(
            f"All {len(df)} rows in this batch failed validation and were quarantined. "
            f"Nothing safe to ingest. See '{quarantine_path}' for reasons."
        )
    return good_df


def flag_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Soft flags retained on surviving rows for downstream visibility --
    distinct from the hard quarantine gate above."""
    check_cols = [c for c in EXPECTED_COLUMNS if c != "cvv" and c in df.columns]
    df["_dq_null_flag"] = df[check_cols].isnull().any(axis=1)
    return df


def ingest(raw_path: str, bronze_path: str, quarantine_path: str = BRONZE_QUARANTINE_PATH) -> pd.DataFrame:
    df = load_raw(raw_path)
    df = validate_schema(df)

    # Hard-drop CVV the moment data lands in the lake -- never persisted,
    # not even in the immutable raw layer.
    cols_to_drop = [c for c in HARD_DROP_ON_INGEST if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    df = quarantine_bad_rows(df, quarantine_path)
    df = flag_data_quality(df)

    df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
    df["_source_system"] = "retail_pos_ecommerce_extract"
    df["_batch_id"] = str(uuid.uuid4())[:8]

    os.makedirs(os.path.dirname(bronze_path) or ".", exist_ok=True)
    df.to_csv(bronze_path, index=False)

    logger.info("Ingested %d valid rows -> %s", len(df), bronze_path)
    logger.info("Hard-dropped on ingest: %s", cols_to_drop)
    logger.info("Rows flagged (soft, non-blocking) for null values: %d", int(df["_dq_null_flag"].sum()))
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    ingest("data/raw_transactions.csv", "bronze/bronze_transactions.csv")
