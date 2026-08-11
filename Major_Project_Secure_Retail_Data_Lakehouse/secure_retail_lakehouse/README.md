# Secure Retail Data Lakehouse

**A compliance-first batch data pipeline that masks, tokenizes, and aggregates retail
PII/PCI data as it moves through Bronze → Silver → Gold layers, so business analysts
get clean spend insights without ever touching a real customer identity.**

Built as part of my Data Engineering internship at Celebal Technologies.

---

## 1. Problem Statement

Retail operational systems (e-commerce platforms, POS networks) constantly generate
raw PII (names, addresses, DOB) and PCI data (card numbers, CVVs). Storing and exposing
this in plain text creates three concrete risks:

| Risk | Example |
|---|---|
| **Security vulnerability** | A breach of raw data directly enables identity theft & financial fraud |
| **Regulatory non-compliance** | Storing CVVs / plain-text identities violates **PCI-DSS**, **GDPR**, **DPDP** |
| **Internal data leaks** | Analysts only need *aggregate* trends, not a customer's home address or phone number — giving them raw access violates least-privilege |

## 2. What This Pipeline Does

A static, automated **batch** pipeline that acts as a strict compliance filter between
operational systems and the analytics team, moving data through three progressively
governed layers:

```
data/raw_transactions.csv   (simulated raw extract — full PII + PCI, plain text)
        │
        ▼
┌───────────────┐   validate schema, tag data-quality issues, stamp lineage metadata.
│    BRONZE     │   Nothing is cleaned — this is the immutable "as received" copy.
└───────────────┘
        │
        ▼
┌───────────────┐   ① Hard-drop CVV outright (PCI-DSS forbids storing it, period)
│    SILVER     │   ② Tokenize name & card number → salted SHA-256 surrogate keys
│  (compliance  │   ③ Mask email & phone → partial, format-preserving reveal
│    filter)    │   ④ Bin exact DOB → age_band, exact amount → spend_category
└───────────────┘   ⑤ Drop free-text address entirely (no analytical value, high risk)
        │
        ▼
┌───────────────┐   Business analytics computed ONLY on tokens + bins.
│     GOLD      │   Total/avg spend by category, per-customer spend (token-ranked),
└───────────────┘   transaction distribution — zero raw identifiers ever surface here.
```

### Why each control exists

| Control | Technique | Why not just "delete the column"? |
|---|---|---|
| CVV | **Hard-drop at Bronze, on ingest** | Zero legitimate use case at any layer — PCI-DSS forbids storing it at all, so it's dropped the moment the batch lands, before it's even written to the raw immutable layer. This is the one field that skips Bronze entirely; every other identifier is retained raw in Bronze and only masked/tokenized/binned at Silver. |
| Name, Card Number | **Salted SHA-256 tokenization** | One-way and irreversible, but *deterministic* — the same person always gets the same token, so analysts can still group/count "unique customers" without ever seeing who they are |
| Email, Phone | **Format-preserving partial mask** | Support/debug workflows sometimes need to eyeball "does this look like a real record" — full tokenization would remove that, so we keep a masked-but-recognizable shape instead |
| Date of Birth | **Binned to age_band** | Trend analysis ("which age group spends more") doesn't need someone's exact birthdate — binning removes re-identification risk while keeping the signal |
| Transaction Amount | **Binned to spend_category** | Lets Gold report Low/Medium/High spend trends without needing per-transaction granularity in every downstream report |
| Address | **Dropped entirely** | No aggregate business question in this project needs an exact street address, and it's one of the highest-risk direct identifiers to retain |

### Before → After (real pipeline output)

**Raw (Bronze-equivalent):**

| customer_name | email | phone | card_number | cvv | dob | amount |
|---|---|---|---|---|---|---|
| Yachana Basak | doctorrachana@example.com | 2859465869 | 5194063336714053 | 349 | 1979-08-11 | 4801.91 |
| Aahana Munshi | jacob50@example.org | 918564078096 | 2714680925961908 | 480 | 2000-08-22 | 3394.04 |

**Silver (post-masking — this is all an analyst ever sees):**

| customer_name_token | email_masked | phone_masked | card_number_token | age_band | spend_category |
|---|---|---|---|---|---|
| TKN_14faaf21618a0ddc | d\*\*\*\*\*\*\*\*\*\*\*\*@example.com | \*\*\*\*\*\*5869 | TKN_52e773d115d96076 | 40-50 | Medium (1000-5000) |
| TKN_e1389ba3ec7649af | j\*\*\*\*\*\*@example.org | \*\*\*\*\*\*\*\*8096 | TKN_4a43db0417e4b928 | 25-30 | Medium (1000-5000) |

## 3. Tech Stack

| Tool | Used for |
|---|---|
| **Python (pandas)** | Core language orchestrating read → transform → write across all three layers |
| **hashlib (SHA-256)** | Salted, one-way tokenization of direct identifiers |
| **Faker** | Generates realistic synthetic PII/PCI so the pipeline is fully runnable without any real customer data |
| **Matplotlib** | Gold-layer business analytics dashboard |
| **Data preprocessing & feature engineering concepts** | Binning (age bands, spend buckets), aggregation, and cleaning applied throughout Silver → Gold |

> In a production deployment this would sit on Azure Data Factory + Delta Lake
> (Bronze/Silver/Gold as managed Delta tables, `HASH_SALT` pulled from Azure Key Vault
> instead of an env var fallback) — the logic in `src/` maps 1:1 onto that architecture,
> just running as local batch scripts for this project.

## 4. Project Structure

```
secure_retail_lakehouse/
├── data/                 # simulated raw operational extract
├── bronze/               # raw ingested + lineage-tagged
├── silver/               # masked / tokenized / binned (safe for analysts)
├── gold/                 # aggregated business analytics + charts + dashboard
├── src/
│   ├── config.py         # masking rules, bins, column lists — single source of truth
│   ├── data_generator.py # synthetic raw data (Faker, en_IN locale)
│   ├── bronze_layer.py   # schema validation + DQ flags + lineage metadata
│   ├── silver_layer.py   # hard-drop / tokenize / mask / bin logic
│   ├── gold_layer.py     # business aggregations + individual charts
│   ├── dashboard.py      # combines the 4 charts into one dashboard image
│   └── main.py           # orchestrates the full pipeline end to end
└── README.md
```

## 5. Running It

```bash
pip install -r requirements.txt
python src/main.py --regen-data     # first run: generates synthetic data + runs full pipeline
python src/main.py                  # subsequent runs: reuses existing raw data
python src/main.py -v               # verbose (DEBUG-level) logging
```

Run the test suite (proves the compliance + error-handling claims below, doesn't just assert them):

```bash
pytest tests/ -v
```

Outputs land in `gold/`:
- `chart_total_vs_avg_by_category.png`
- `chart_avg_spend_per_customer.png`
- `chart_total_spend_by_customer.png`
- `chart_transaction_distribution.png`
- `gold_layer_dashboard.png` (all four combined)
- `customer_spend_summary.csv`, `total_vs_avg_by_category.csv`, `transaction_distribution.csv`

## 6. Error Handling & Data Quality

A batch pipeline that crashes on the first malformed row isn't production-grade, so
every layer is defensive:

| Failure | Handling |
|---|---|
| Raw source file missing / empty / unparseable | `SourceFileError` raised with a specific, actionable message — not a raw pandas traceback |
| Required column missing from the source schema | `SchemaValidationError` naming exactly which columns are missing |
| A row has a null in a required field, a negative/non-numeric amount, an unparseable date, or a duplicate `transaction_id` | **Quarantined**, not dropped silently and not allowed to crash the batch — written to `bronze/quarantined_rows.csv` with a `_quarantine_reason` column, while the rest of the batch proceeds |
| Every row in a batch fails validation | `NoValidRowsError` — the pipeline stops rather than silently writing an empty file downstream |
| A raw PII/PCI column somehow survives all the way through Silver's transforms (e.g. a future code edit accidentally breaks a drop step) | `assert_no_pii_leakage()` runs after every transform and raises `PIILeakageError`, refusing to write output — this is the last line of defense, not the primary control |
| DOB in an unexpected but valid format | Retried with a fallback parser before falling back to an explicit `"Unknown"` age band (row is kept, not dropped) |
| A spend category has zero transactions in a given batch | Charts/aggregates show it as 0 rather than the category silently disappearing |
| Misconfigured bins in `config.py` (mismatched bin/label counts, non-ascending edges) | Fails at **import time**, before any data is touched |

All of this is proven by `tests/test_pipeline.py` (22 tests) — including deliberately
injecting negative amounts, non-numeric amounts, nulls, garbage dates, duplicate IDs,
and a simulated PII leak, and asserting the pipeline reacts correctly to each one rather
than crashing or silently corrupting output. `src/main.py` also exits with a distinct
non-zero code (`1` for a known data/pipeline issue, `2` for an unexpected bug) so a
scheduler could act on the difference.

## 7. What I'd Add With More Time

- Swap the local CSV "layers" for actual **Delta Lake** tables with `MERGE`-based
  upserts, so re-running the pipeline is idempotent instead of overwrite-based.
- Move `HASH_SALT` to **Azure Key Vault** and rotate it on a schedule, re-tokenizing
  affected rows.
- Add a **PySpark** version of `silver_layer.py` for when raw volume outgrows pandas.
- Row-level access control on Silver (e.g. only fraud/risk team can see
  `card_number_token`, general analysts get spend aggregates only).
- An actual scheduler/trigger (cron, Airflow, or an ADF pipeline trigger) — right now
  this is a script that's run on demand; the batch *logic* is automated, the *trigger*
  isn't yet.

