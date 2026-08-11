"""
test_pipeline.py
----------------
Automated proof of the pipeline's core guarantees -- not just "it runs",
but the specific compliance claims made in the README:

  - tokenization is deterministic and irreversible-looking
  - CVV never survives past Bronze ingestion
  - no raw PII column ever reaches Silver output
  - malformed rows are quarantined, not silently dropped or crash-inducing
  - Gold aggregates are numerically correct on a known small dataset

Run with:  pytest tests/ -v
(run from the project root, with the venv active)
"""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import bronze_layer  # noqa: E402
import gold_layer  # noqa: E402
import silver_layer  # noqa: E402
from exceptions import (  # noqa: E402
    NoValidRowsError, PIILeakageError, SchemaValidationError, SourceFileError,
)


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def sample_raw_df():
    return pd.DataFrame({
        "transaction_id": ["TXN001", "TXN002", "TXN003"],
        "customer_id": ["CUST001", "CUST002", "CUST001"],
        "customer_name": ["Aisha Khan", "Rohan Verma", "Aisha Khan"],
        "email": ["aisha@example.com", "rohan@example.com", "aisha@example.com"],
        "phone": ["9876543210", "9123456780", "9876543210"],
        "address": ["123 MG Road, Pune", "45 Park St, Kolkata", "123 MG Road, Pune"],
        "date_of_birth": ["1995-06-15", "1988-02-20", "1995-06-15"],
        "card_number": ["4111111111111111", "5500000000000004", "4111111111111111"],
        "cvv": ["123", "456", "123"],
        "transaction_amount": [500.0, 3000.0, 8000.0],
        "transaction_date": ["2026-01-10", "2026-01-11", "2026-01-12"],
        "store_channel": ["E-Commerce", "POS-Store", "E-Commerce"],
    })


@pytest.fixture
def tmp_paths(tmp_path):
    return {
        "raw": str(tmp_path / "raw.csv"),
        "bronze": str(tmp_path / "bronze.csv"),
        "quarantine": str(tmp_path / "quarantine.csv"),
        "silver": str(tmp_path / "silver.csv"),
        "gold": str(tmp_path / "gold"),
    }


# --------------------------------------------------------------------------
# Tokenization / masking correctness
# --------------------------------------------------------------------------

class TestTokenizationAndMasking:
    def test_tokenize_is_deterministic(self):
        t1 = silver_layer.tokenize("Aisha Khan")
        t2 = silver_layer.tokenize("Aisha Khan")
        assert t1 == t2

    def test_tokenize_different_inputs_differ(self):
        assert silver_layer.tokenize("Aisha Khan") != silver_layer.tokenize("Rohan Verma")

    def test_tokenize_does_not_contain_original_value(self):
        token = silver_layer.tokenize("Aisha Khan")
        assert "Aisha" not in token
        assert "Khan" not in token

    def test_tokenize_handles_nan(self):
        assert silver_layer.tokenize(float("nan")) is None

    def test_mask_email_partially_reveals(self):
        masked = silver_layer.mask_email("aisha@example.com")
        assert masked.startswith("a")
        assert "aisha" not in masked
        assert masked.endswith("@example.com")

    def test_mask_phone_keeps_last_four_only(self):
        masked = silver_layer.mask_phone("9876543210")
        assert masked.endswith("3210")
        assert "987654" not in masked


# --------------------------------------------------------------------------
# Bronze: hard-drop, schema validation, quarantine
# --------------------------------------------------------------------------

class TestBronzeLayer:
    def test_cvv_dropped_immediately_on_ingest(self, sample_raw_df, tmp_paths):
        sample_raw_df.to_csv(tmp_paths["raw"], index=False)
        result = bronze_layer.ingest(tmp_paths["raw"], tmp_paths["bronze"], tmp_paths["quarantine"])
        assert "cvv" not in result.columns

        bronze_on_disk = pd.read_csv(tmp_paths["bronze"])
        assert "cvv" not in bronze_on_disk.columns

    def test_missing_source_file_raises_specific_error(self, tmp_paths):
        with pytest.raises(SourceFileError):
            bronze_layer.ingest("does/not/exist.csv", tmp_paths["bronze"], tmp_paths["quarantine"])

    def test_empty_source_file_raises_specific_error(self, tmp_paths):
        open(tmp_paths["raw"], "w").close()
        with pytest.raises(SourceFileError):
            bronze_layer.ingest(tmp_paths["raw"], tmp_paths["bronze"], tmp_paths["quarantine"])

    def test_missing_required_column_raises_schema_error(self, sample_raw_df, tmp_paths):
        sample_raw_df.drop(columns=["email"]).to_csv(tmp_paths["raw"], index=False)
        with pytest.raises(SchemaValidationError):
            bronze_layer.ingest(tmp_paths["raw"], tmp_paths["bronze"], tmp_paths["quarantine"])

    def test_negative_amount_is_quarantined_not_crashed(self, sample_raw_df, tmp_paths):
        sample_raw_df.loc[0, "transaction_amount"] = -500
        sample_raw_df.to_csv(tmp_paths["raw"], index=False)
        result = bronze_layer.ingest(tmp_paths["raw"], tmp_paths["bronze"], tmp_paths["quarantine"])
        assert len(result) == 2  # 1 quarantined, 2 survive
        quarantined = pd.read_csv(tmp_paths["quarantine"])
        assert len(quarantined) == 1
        assert "invalid_or_negative_amount" in quarantined["_quarantine_reason"].iloc[0]

    def test_duplicate_transaction_id_is_quarantined(self, sample_raw_df, tmp_paths):
        sample_raw_df.loc[1, "transaction_id"] = sample_raw_df.loc[0, "transaction_id"]
        sample_raw_df.to_csv(tmp_paths["raw"], index=False)
        result = bronze_layer.ingest(tmp_paths["raw"], tmp_paths["bronze"], tmp_paths["quarantine"])
        assert len(result) == 2
        assert result["transaction_id"].is_unique

    def test_all_rows_bad_raises_no_valid_rows_error(self, sample_raw_df, tmp_paths):
        sample_raw_df["transaction_amount"] = -1  # every row now invalid
        sample_raw_df.to_csv(tmp_paths["raw"], index=False)
        with pytest.raises(NoValidRowsError):
            bronze_layer.ingest(tmp_paths["raw"], tmp_paths["bronze"], tmp_paths["quarantine"])


# --------------------------------------------------------------------------
# Silver: PII leakage guard + binning correctness
# --------------------------------------------------------------------------

class TestSilverLayer:
    def test_full_transform_leaves_no_raw_pii(self, sample_raw_df, tmp_paths):
        sample_raw_df.to_csv(tmp_paths["raw"], index=False)
        bronze_layer.ingest(tmp_paths["raw"], tmp_paths["bronze"], tmp_paths["quarantine"])
        result = silver_layer.transform(tmp_paths["bronze"], tmp_paths["silver"])

        for raw_col in ["customer_name", "email", "phone", "address", "date_of_birth", "card_number", "cvv"]:
            assert raw_col not in result.columns

    def test_leakage_guard_fires_on_injected_raw_column(self):
        bad_df = pd.DataFrame({"email": ["leaked@example.com"], "transaction_amount": [500]})
        with pytest.raises(PIILeakageError):
            silver_layer.assert_no_pii_leakage(bad_df)

    def test_spend_bucketing_matches_business_definition(self):
        df = pd.DataFrame({"transaction_amount": [500, 2500, 9000]})
        result = silver_layer.bin_spend(df)
        assert list(result["spend_category"]) == ["Low (<1000)", "Medium (1000-5000)", "High (>5000)"]

    def test_unparseable_dob_gets_unknown_band_not_dropped_silently(self):
        df = pd.DataFrame({"date_of_birth": ["not-a-date", "1990-01-01"]})
        result = silver_layer.bin_age(df)
        assert result["age_band"].iloc[0] == "Unknown"
        assert len(result) == 2  # row is not dropped

    def test_missing_bronze_file_raises_specific_error(self, tmp_paths):
        with pytest.raises(SourceFileError):
            silver_layer.transform("does/not/exist.csv", tmp_paths["silver"])


# --------------------------------------------------------------------------
# Gold: aggregation correctness on a known dataset
# --------------------------------------------------------------------------

class TestGoldLayer:
    def test_total_vs_avg_matches_hand_calculated_values(self, tmp_paths):
        silver_df = pd.DataFrame({
            "customer_name_token": ["TKN_a", "TKN_b", "TKN_a"],
            "transaction_amount": [500, 2000, 6000],
            "spend_category": ["Low (<1000)", "Medium (1000-5000)", "High (>5000)"],
        })
        os.makedirs(tmp_paths["gold"], exist_ok=True)
        silver_df.to_csv(tmp_paths["silver"], index=False)

        summary, customer_stats, counts = gold_layer.run(tmp_paths["silver"], tmp_paths["gold"])

        assert summary.loc["Low (<1000)", "total_amount"] == 500
        assert summary.loc["Medium (1000-5000)", "total_amount"] == 2000
        assert summary.loc["High (>5000)", "total_amount"] == 6000
        assert customer_stats.loc["TKN_a", "total_amount"] == 6500  # 500 + 6000
        assert counts["Low (<1000)"] == 1

    def test_missing_silver_file_raises_specific_error(self, tmp_paths):
        with pytest.raises(SourceFileError):
            gold_layer.run("does/not/exist.csv", tmp_paths["gold"])

    def test_missing_required_column_raises_schema_error(self, tmp_paths):
        pd.DataFrame({"transaction_amount": [100]}).to_csv(tmp_paths["silver"], index=False)
        with pytest.raises(SchemaValidationError):
            gold_layer.run(tmp_paths["silver"], tmp_paths["gold"])


# --------------------------------------------------------------------------
# End-to-end integration
# --------------------------------------------------------------------------

class TestEndToEnd:
    def test_full_pipeline_runs_and_produces_gold_outputs(self, sample_raw_df, tmp_paths):
        sample_raw_df.to_csv(tmp_paths["raw"], index=False)
        bronze_layer.ingest(tmp_paths["raw"], tmp_paths["bronze"], tmp_paths["quarantine"])
        silver_layer.transform(tmp_paths["bronze"], tmp_paths["silver"])
        gold_layer.run(tmp_paths["silver"], tmp_paths["gold"])

        assert os.path.exists(os.path.join(tmp_paths["gold"], "chart_total_vs_avg_by_category.png"))
        assert os.path.exists(os.path.join(tmp_paths["gold"], "customer_spend_summary.csv"))
