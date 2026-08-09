<div align="center">

# Celebal Technologies — Data Engineering Internship

### CEI Program · Data Engineering Track

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat-square&logo=postgresql&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-E25A1C?style=flat-square&logo=apachespark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-00ADD8?style=flat-square&logo=delta&logoColor=white)
![Azure](https://img.shields.io/badge/Azure%20Data%20Factory-0078D4?style=flat-square&logo=microsoftazure&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

A week-by-week record of my Data Engineering internship — from Pandas fundamentals to Spark internals, Delta Lake, and a full end-to-end analytics system.

</div>

---

## 📖 About this repository

This repo documents everything built during the **Celebal Excellence Intern (CEI) Program — Data Engineering Track**. Each week is a self-contained folder with its own notebook/script, dataset reference, and README covering the objective, approach, and results.

The work progresses deliberately: **Python/Pandas fundamentals → SQL analytics → cloud pipelines (Azure Data Factory) → distributed processing (PySpark) → Spark internals → transactional data lakes (Delta Lake) → a full production-style analytics system (Python + SQL, end to end)**.

---

## 🗂️ Weekly Index

| # | Topic | Core Skills | Status |
|---|---|---|:---:|
| 1 | Data Exploration & Cleaning with Pandas | Pandas, data cleaning | ✅ |
| 2 | ShopEase E-commerce DB Analysis | SQL fundamentals | ✅ |
| 3 | Superstore Sales Analysis | Subqueries, CTEs, Window Functions | ✅ |
| 4 | Azure Data Factory Pipeline | ADF, Get Metadata, Copy Data | ✅ |
| 5 | Spark Fundamentals | PySpark, cleaning, aggregation | ✅ |
| 6 | Spark Architecture Deep Dive | Lazy eval, DAGs, Parquet vs CSV | ✅ |
| 7 | Delta Lake MERGE | Delta Lake, upserts, ACID | ✅ |
| 8 | **E-Commerce Order Analytics System** | Python, SQL, data cleaning, CLI tooling | ✅ ⭐ |

---

## 🧠 Skills demonstrated across the internship

<table>
<tr>
<td valign="top" width="33%">

**Data Engineering**
- ETL pipeline design
- Data cleaning & validation
- Referential integrity checks
- Incremental / upsert processing

</td>
<td valign="top" width="33%">

**SQL**
- CTEs (single & multi-level)
- Window functions (`RANK`, `DENSE_RANK`, `NTILE`, `LAG`/`LEAD`)
- Cohort & retention analysis
- Self-joins, subqueries

</td>
<td valign="top" width="33%">

**Big Data & Cloud**
- PySpark DataFrame API
- Spark execution model (DAGs, lazy eval)
- Delta Lake transactions
- Azure Data Factory pipelines

</td>
</tr>
</table>

---

## ⭐ Featured Project: Week 8 — E-Commerce Order Analytics System

The most complete build in this repo — a full pipeline, not a single script.

```
Generate (intentionally messy data) → Clean → Load into SQLite → 16 SQL Analyses → CLI Reporting Tool
```

**What sets it apart:**
- Data quality issues are **injected on purpose during generation** — missing foreign keys, malformed dates, invalid emails — then genuinely detected and handled downstream, not hand-waved.
- **16 SQL queries**, basic through advanced: `DENSE_RANK`, `NTILE`, `LAG`/`LEAD`, multi-level CTEs, cohort retention, YoY comparisons.
- A **working CLI report tool** (stdlib-only, no pandas) that generates orders/revenue/top-products reports with period-over-period comparison.
- **Real unit tests** covering 4 edge cases — broken foreign keys, invalid discounts, zero quantities, future-dated orders.
- Runs end to end with one command:
  ```bash
  cd Week8 && pip install -r requirements.txt && bash run_pipeline.sh
  ```

**Results from the last full run:**

| Check | Result |
|---|---|
| Missing `customer_id` detected | 114 orders (~5%) — flagged, not dropped |
| Wrong date format corrected | 99 rows normalized (`DD-MM-YYYY` → standard) |
| Returns flagged (negative qty) | 209 line items |
| Invalid emails detected | 9 customers |
| Intentional broken foreign keys caught | 6 / 6 |
| SQL queries executed successfully | 16 / 16 |

📄 Full design write-up and rationale: [`Week8/README.md`](./Week8/README.md)

---

## 📌 Week 1 — Basic Data Exploration & Cleaning using Pandas

Introductory Python + Pandas assignment covering the fundamentals of loading, exploring, and cleaning a raw dataset before analysis.

**Objective:** Learn Python basics and perform basic data exploration and cleaning using Pandas.

**Steps Covered:**

1. Load a CSV dataset into a Pandas DataFrame
2. Explore data — `.head()`/`.tail()`, `.shape`, `.columns`, `.dtypes`
3. Handle missing values — identify, fill/drop as appropriate
4. Perform basic operations — filter rows, select columns
5. Remove duplicate records
6. Create a derived column — `total_amount = price * quantity`
7. Export the cleaned dataset as a new CSV file

**Output:** Jupyter Notebook (`.ipynb`) + cleaned CSV + brief summary

---

## 📌 Week 2 — ShopEase E-commerce Database Analysis

SQL fundamentals assignment building and querying an e-commerce database (`ShopEase`).

---

## 📌 Week 3 — Superstore Sales Analysis

SQL-based analysis of the Superstore dataset applying subqueries, CTEs, and window functions to derive customer sales insights.

**Key Insights:**

- Top customer (Sean Miller) generated **$25,043.05** in total sales
- **12 customers** placed only one order and never returned
- Average customer spend: **$2,896.85**, with only **294/793 (~37%)** above average

---

## 📌 Week 4 — Azure Data Factory: End-to-End Pipeline

Built an end-to-end data pipeline on Azure using Azure Storage Account and Azure Data Factory, applied to the Superstore dataset.

**Objective:** Learn cloud-based data engineering fundamentals — provisioning storage, building ADF pipelines, and orchestrating data movement.

**Steps Covered:**

1. Set up an Azure Storage Account and container for the Superstore dataset
2. Built pipeline `pl_superstore_pipeline` in Azure Data Factory
3. Used **Get Metadata** activity to validate file existence/structure before processing
4. Used **Copy Data** activity to move data between storage locations
5. Debugged subscription-policy restrictions on new student accounts, resolved via a personal Azure Free Trial account

**Output:** ADF pipeline (JSON export) + screenshots of pipeline run + brief summary

---

## 📌 Week 5 — Spark Fundamentals: Data Cleaning & Aggregation

PySpark-based assignment covering Spark fundamentals and hands-on DataFrame cleaning, transformation, and aggregation on a real Kaggle e-commerce dataset.

**Objective:** Understand Spark's in-memory architecture over traditional MapReduce, and apply PySpark DataFrames for cleaning, filtering, and aggregating data.

**Dataset:** [E-Commerce Transactions Dataset](https://www.kaggle.com/datasets/smayanj/e-commerce-transactions-dataset) (Kaggle, 50K rows)

**Steps Covered:**

1. MapReduce limitations vs Spark's in-memory computing (conceptual)
2. DataFrame immutability and its effect on cleaning pipelines (conceptual)
3. Deduplication using `dropDuplicates()`
4. Null detection across all columns + handling via `.na.drop()` / `.na.fill()`
5. Conditional filtering (age range + category/subscription-tier equivalents)
6. GroupBy aggregations using `.agg()` — min, max, mean, sum
7. Shuffle process and wide vs narrow transformations (conceptual)
8. Multi-format timestamp casting via `try_to_timestamp` + `coalesce`
9. Risks of `inferSchema=True` on inconsistent date formats (conceptual)
10. Final chained pipeline: dedup → fill nulls → aggregate revenue by category

**Key Insights:**

- Removed **13,846 duplicate rows** out of 50,000
- **Books** was the top-revenue category (~₹23.2L)
- Achieved **0 failed timestamp casts** using explicit multi-format parsing instead of relying on `inferSchema`

**Output:** Jupyter Notebook (`.ipynb`) with executed outputs + brief summary

---

## 📌 Week 6 — Spark Architecture: Lazy Evaluation, DAGs & File Format Tradeoffs

Conceptual + applied deep-dive into how Spark actually executes a job under the hood, building on Week 5's hands-on PySpark work.

**Objective:** Understand Spark's execution model — transformations vs actions, lazy evaluation, the DAG/lineage graph — and reason about storage format tradeoffs for analytical workloads.

**Topics Covered:**

1. Transformations vs actions, and why Spark defers execution until an action is called
2. Lazy evaluation — how it enables query optimization before any computation runs
3. DAG (Directed Acyclic Graph) construction and lineage tracking for fault tolerance
4. Predicate pushdown — filtering at the storage layer instead of after loading
5. CSV vs Parquet — columnar storage, compression, schema enforcement, and read/write performance tradeoffs

**Output:** Jupyter Notebook (`.ipynb`) with executed outputs + brief summary

---

## 📌 Week 7 — Delta Lake MERGE Implementation

Incremental data processing using Delta Lake, applied to the Superstore dataset, reshaped into a realistic upsert scenario.

**Objective:** Perform incremental data processing using Delta Lake.

**Approach:** the static Superstore file is split 85/15 — 8,495 rows become the "already loaded" Delta table, 1,499 held back to simulate orders not yet in the system. The incremental batch then combines **425 order corrections** (existing orders with a retroactive discount/profit adjustment) and **300 new orders** pulled from the holdout pool.

**Steps Covered:**

1. Load the dataset into a Delta table (`deltalake` / delta-rs — the native Python Delta Lake engine)
2. Basic cleaning — audited for nulls/duplicates (genuinely 0 of either in this file)
3. Build the incremental dataset (corrections + new orders)
4. Apply a `MERGE` — `when_matched_update_all()` + `when_not_matched_insert_all()`
5. Validate results — row counts, duplicate check, before/after profit comparison
6. Display the final dataset and Delta's transaction history

**Key Insights:**

- Final table: **8,795 rows** (8,495 + 300 inserts, exactly as expected)
- **0 duplicate `Row_ID`s** after merge
- Profit on corrected orders moved from **$15,113.30 → $26,724.45** (net **+$11,611.15**), confirming the update half of the merge took effect, not just the insert half

**Output:** Jupyter Notebook (`.ipynb`) with executed outputs + screenshots + short explanation

---

## 📌 Week 8 — E-Commerce Order Analytics System

A full mini end-to-end analytics pipeline, not a single script: synthetic (intentionally messy) data → cleaned data → SQLite → 16 SQL analyses → a CLI reporting tool, tying together everything from Weeks 1–7 (Pandas cleaning, SQL window functions/CTEs, and a proper local database) into one project.

**Objective:** Simulate joining a company with messy, multi-source order data — clean it, model it relationally, and answer real business questions against it using SQL alone (no shortcuts through pandas for the analysis layer).

**Approach:** Rather than generating clean data and sprinkling in a few nulls afterward, data quality issues are injected *during* generation and then have to be genuinely detected and handled downstream — including a small, fixed number of intentionally broken foreign keys, so the referential-integrity checker has something real to catch instead of trivially passing on data that was never going to break it.

**Steps Covered:**

1. Generate 4 relational CSVs (`customers`, `products`, `orders`, `order_items`) with realistic fake data and deliberate issues: missing `customer_id`, malformed date formats, messy product name casing, invalid emails, negative quantities (returns)
2. `clean_orders()` / `clean_products()` / `validate_emails()` / `check_referential_integrity()` — fix what's fixable (date formats, name casing), flag what isn't (missing FK, bad email) rather than deleting rows outright
3. Load cleaned data into a local SQLite database with indexes on every join/filter column
4. **16 SQL queries** — basic (revenue per category, top customers, monthly order counts) through advanced (running totals, `DENSE_RANK`, `LAG`/`LEAD` gap analysis, multi-level CTEs, `NTILE` quartile segmentation, YoY comparison, cohort retention, self-join "frequently bought together")
5. A command-line report tool (stdlib only — `sqlite3` + `argparse`, no pandas) that takes a report type + date range and returns totals, top products, and % change vs. the previous period
6. Unit tests for 4 explicit edge cases: orphan foreign keys, out-of-range discounts, zero quantity, future-dated orders

**Key Insights:**

- **114 orders (~5%)** had a missing `customer_id` — kept, not dropped, since a missing FK doesn't mean the order didn't happen
- **99 dates** were caught in the wrong format (`DD-MM-YYYY`) and normalized without guessing
- **209 order line items** were flagged as returns (negative quantity) — included in revenue calculations on purpose, since a return should reduce recognized revenue, not disappear from it
- **6/6 intentionally broken foreign keys** were caught and removed by `check_referential_integrity()` — proof the checker actually works, not just that it runs
- All 16 SQL queries executed successfully against the cleaned dataset, including window-function and cohort-analysis queries validated against a real (if synthetic) 2-year order history

**Output:** Full project folder (`src/`, `sql/`, `tests/`, generated `data/`, `reports/`, `query_results/`) + one-command pipeline runner (`run_pipeline.sh`) + project-level `README.md` with design rationale

---

## 🔄 How this repo is updated

A new folder is added each week with that week's assignment, following the same structure: notebook/script + dataset reference + brief README summarizing objective, techniques used, and insights.

---

<div align="center">

## 🙋 About Me

**Piyush Pankaj** · Final-year B.Tech CSE, DIT University Dehradun (2023–2027)
Data Engineering Intern @ Celebal Technologies (CEI Program)

[![GitHub](https://img.shields.io/badge/GitHub-piyush23--eng-181717?style=flat-square&logo=github)](https://github.com/piyush23-eng)


</div>
