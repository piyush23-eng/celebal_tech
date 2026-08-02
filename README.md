# 📊 Celebal Technologies — Data Engineering Internship (CEI)

This repository contains my weekly assignment submissions for the **Celebal Excellence Intern (CEI) Program — Data Engineering Track**.

Each week's work is organized into its own folder with the relevant notebook/script, dataset reference, and a brief summary of what was covered.

---

## 📅 Weekly Assignments

| Week   | Topic                                                              | Status      |
| ------ | ------------------------------------------------------------------- | ----------- |
| Week 1 | Basic Data Exploration & Cleaning using Pandas                     | ✅ Completed |
| Week 2 | E-commerce Database Analysis (ShopEase) — SQL Fundamentals         | ✅ Completed |
| Week 3 | Superstore Sales Analysis — Subqueries, CTEs & Window Functions    | ✅ Completed |
| Week 4 | Azure Data Factory — End-to-End Pipeline (Superstore)              | ✅ Completed |
| Week 5 | Spark Fundamentals — Data Cleaning & Aggregation                   | ✅ Completed |
| Week 6 | Spark Architecture — Lazy Evaluation, DAGs & File Format Tradeoffs | ✅ Completed |
| Week 7 | Pandas Revisited — Deeper Data Cleaning & EDA (Superstore)         | ✅ Completed |

---

## 🛠️ Tech Stack

- **Python** (pandas, PySpark)
- **SQL** (SQLite / MySQL)
- **Apache Spark** (PySpark, local mode)
- **Azure** (Storage Account, Data Factory)
- **Google Colab**
- **Git & GitHub** for version control

Each week's folder has its own `README.md` with objective, approach, and key takeaways specific to that assignment — this top-level README just links everything together.

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

## 📌 Week 7 — Pandas Revisited: Deeper Data Cleaning & EDA (Latest)

A second pass at Python + Pandas fundamentals — same core skill set as Week 1, but pushed further: deliberate data-quality simulation, column-appropriate cleaning strategies, and a validated derived column, applied to the full Superstore dataset (9,994 rows).

**Objective:** Perform data exploration and cleaning using Pandas, and validate every cleaning decision rather than assuming it's correct.

**Steps Covered:**

1. Load the CSV and profile it — `.head()`/`.tail()`, `.shape`, `.columns`, `.dtypes`, `.describe()`
2. Audit data quality on the raw file (0 nulls, 0 duplicates as delivered)
3. Simulate realistic messiness on a seeded copy — missing values, duplicate rows, inconsistent category casing — to properly exercise the cleaning workflow
4. Handle missing values with column-appropriate strategies (group-median impute, row drop, mode fill) instead of one blanket rule
5. Standardize inconsistent category labels and remove duplicate rows
6. Filter rows (high-value loss-making orders, region + segment slices) and select columns
7. Derive `Price` (unit price) and `total_amount = Price * Quantity`, validated against `Sales`
8. Quick EDA — sales by category, profit by region, top 10 products by revenue
9. Export the cleaned dataset to a new CSV file

**Key Insights:**

- Technology and Office Supplies lead total sales; Furniture lags behind
- **Central** region shows the weakest profit performance; **West** is the strongest
- A small set of products account for a disproportionate share of top-line sales

**Output:** Jupyter Notebook (`.ipynb`) with executed outputs + cleaned CSV + brief summary

---

## 🙋 About

Data Engineering Intern @ Celebal Technologies (CEI Program)
Final-year B.Tech CSE student, DIT University Dehradun

---

## 🔄 How This Repo Is Updated

A new folder is added each week with that week's assignment, following the same structure: notebook + dataset reference + brief README summarizing objective, techniques used, and insights.
