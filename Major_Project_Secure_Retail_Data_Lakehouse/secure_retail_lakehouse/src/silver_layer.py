"""
silver_layer.py
----------------
SILVER LAYER = the compliance filter -- hardened.

Every transformation here maps to a specific risk called out in the
problem statement:

  1. HARD-DROP   -> cvv is physically deleted -- but that already
                     happened one layer earlier, in Bronze, at the point
                     of ingestion (see bronze_layer.py). By the time data
                     reaches Silver, CVV is already gone; there is
                     nothing left to drop here. Kept as a defensive
                     no-op below so nothing can slip through even if
                     Silver is ever called on data that skipped Bronze.
  2. TOKENIZE     -> customer_name & card_number are replaced with a
                     salted SHA-256 token. One-way and irreversible, but
                     STABLE -- the same input always produces the same
                     token, so analysts can group/join on "same person"
                     without ever seeing who that person actually is.
  3. MASK          -> email / phone are format-preserving masked
                     (partial reveal) so a support/debug workflow can
                     still eyeball "does this look like a valid
                     record", without exposing the full identifier.
  4. BIN/AGGREGATE -> exact date_of_birth -> age_band, exact
                     transaction_amount -> spend_category. Lets Gold do
                     trend analysis without exposing one specific
                     customer's exact age or exact spend.

Address is dropped entirely at Silver -- no legitimate use case for
aggregate business analytics, and one of the highest-risk direct
identifiers to retain.

SAFETY NET: after every transform, `assert_no_pii_leakage()` checks
that none of the raw identifier columns survived. If a future edit to
this file accidentally stops dropping one of them, the pipeline fails
loudly here instead of silently shipping PII to Gold.
"""

import hashlib
import logging
import os

import pandas as pd

from config import (
    AGE_BINS, AGE_LABELS, HARD_DROP_COLUMNS, HASH_SALT,
    RAW_PII_COLUMNS, SPEND_BINS, SPEND_LABELS, TOKENIZE_COLUMNS,
)
from exceptions import PIILeakageError, SourceFileError

logger = logging.getLogger("lakehouse.silver")


def tokenize(value) -> str:
    """One-way salted SHA-256 tokenization. Deterministic, irreversible.
    Handles missing/NaN and non-string input defensively -- a malformed
    upstream value should not crash the whole batch."""
    if pd.isna(value):
        return None
    salted = f"{HASH_SALT}:{str(value)}".encode("utf-8")
    return "TKN_" + hashlib.sha256(salted).hexdigest()[:16]


def mask_email(email) -> str:
    if pd.isna(email) or "@" not in str(email):
        return None
    local, domain = str(email).split("@", 1)
    visible = local[0] if local else "*"
    return f"{visible}{'*' * max(len(local) - 1, 1)}@{domain}"


def mask_phone(phone) -> str:
    if pd.isna(phone):
        return None
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(digits) < 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]


def hard_drop(df: pd.DataFrame) -> pd.DataFrame:
    """Defensive no-op by the time Silver runs -- CVV is already gone as
    of Bronze ingestion. Kept here so CVV still can't slip through if
    this function is ever called on data that bypassed Bronze."""
    cols_present = [c for c in HARD_DROP_COLUMNS if c in df.columns]
    return df.drop(columns=cols_present)


def apply_tokenization(df: pd.DataFrame) -> pd.DataFrame:
    for col in TOKENIZE_COLUMNS:
        if col in df.columns:
            df[f"{col}_token"] = df[col].apply(tokenize)
            df = df.drop(columns=[col])
    return df


def apply_masking(df: pd.DataFrame) -> pd.DataFrame:
    if "email" in df.columns:
        df["email_masked"] = df["email"].apply(mask_email)
        df = df.drop(columns=["email"])
    if "phone" in df.columns:
        df["phone_masked"] = df["phone"].apply(mask_phone)
        df = df.drop(columns=["phone"])
    return df


def bin_age(df: pd.DataFrame) -> pd.DataFrame:
    if "date_of_birth" not in df.columns:
        return df
    dob = pd.to_datetime(df["date_of_birth"], format="%Y-%m-%d", errors="coerce")
    # A handful of rows may use a different but still valid format (e.g.
    # if a source system sends DD-MM-YYYY) -- retry those specifically
    # rather than writing everything off as "Unknown".
    still_missing = dob.isna() & df["date_of_birth"].notna()
    if still_missing.any():
        dob.loc[still_missing] = pd.to_datetime(
            df.loc[still_missing, "date_of_birth"], errors="coerce"
        )
    today = pd.Timestamp.today()
    age = (today - dob).dt.days // 365
    # Rows with an unparseable DOB get an explicit "Unknown" band rather
    # than silently becoming NaN and disappearing from Gold aggregates.
    df["age_band"] = pd.cut(age, bins=AGE_BINS, labels=AGE_LABELS, right=False)
    df["age_band"] = df["age_band"].astype("object")
    df.loc[dob.isna(), "age_band"] = "Unknown"
    return df.drop(columns=["date_of_birth"])


def bin_spend(df: pd.DataFrame) -> pd.DataFrame:
    amount = pd.to_numeric(df["transaction_amount"], errors="coerce")
    df["spend_category"] = pd.cut(amount, bins=SPEND_BINS, labels=SPEND_LABELS, right=False)
    return df


def drop_high_risk_freeform(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["address"], errors="ignore")


def drop_bronze_metadata(df: pd.DataFrame) -> pd.DataFrame:
    meta_cols = [c for c in df.columns if c.startswith("_")]
    return df.drop(columns=meta_cols, errors="ignore")


def assert_no_pii_leakage(df: pd.DataFrame) -> None:
    """Last line of defense: if any raw identifier column is still
    present after all transforms have run, stop the pipeline instead of
    writing a PII-bearing file to Silver. This should never fire under
    normal operation -- it exists purely to catch a future regression."""
    leaked = [c for c in RAW_PII_COLUMNS if c in df.columns]
    if leaked:
        raise PIILeakageError(
            f"PII leakage detected in Silver output -- raw identifier column(s) "
            f"survived transformation: {leaked}. Refusing to write output. "
            f"This indicates a bug in silver_layer.py, not bad input data."
        )


def transform(bronze_path: str, silver_path: str) -> pd.DataFrame:
    if not os.path.exists(bronze_path):
        raise SourceFileError(
            f"Bronze file not found: '{bronze_path}'. Run bronze_layer.ingest() first."
        )
    df = pd.read_csv(bronze_path)
    if df.empty:
        raise SourceFileError(f"Bronze file '{bronze_path}' contains 0 rows -- nothing to transform.")

    df = hard_drop(df)
    df = drop_high_risk_freeform(df)
    df = apply_tokenization(df)
    df = apply_masking(df)
    df = bin_age(df)
    df = bin_spend(df)
    df = drop_bronze_metadata(df)

    assert_no_pii_leakage(df)

    os.makedirs(os.path.dirname(silver_path) or ".", exist_ok=True)
    df.to_csv(silver_path, index=False)
    logger.info("Transformed %d rows -> %s", len(df), silver_path)
    logger.info("Columns retained: %s", list(df.columns))
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    transform("bronze/bronze_transactions.csv", "silver/silver_transactions.csv")
