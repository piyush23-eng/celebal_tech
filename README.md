# 📊 Celebal Technologies — Data Engineering Internship (CEI)

This repository contains my weekly assignment submissions for the **Celebal Excellence Intern (CEI) Program — Data Engineering Track**.

Each week's work is organized into its own folder with the relevant notebook/script, dataset reference, and a brief summary of what was covered.

---

## 📅 Weekly Assignments

| Week | Topic | Status |
|------|-------|--------|
| Week 1 | Basic Data Exploration & Cleaning using Pandas | ✅ Completed |
| Week 2 | E-commerce Database Analysis (ShopEase) — SQL Fundamentals | ✅ Completed |
| Week 3 | Superstore Sales Analysis — Subqueries, CTEs & Window Functions | ✅ Completed |
| Week 4 | Azure Data Factory — End-to-End Pipeline (Superstore) | ✅ Completed |
| Week 5 | Spark Fundamentals — Data Cleaning & Aggregation | ✅ Completed |

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

## 📌 Week 5 — Spark Fundamentals: Data Cleaning & Aggregation (Latest)

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

## 🙋 About

Data Engineering Intern @ Celebal Technologies (CEI Program)
Final-year B.Tech CSE student, DIT University Dehradun

---

## 🔄 How This Repo Is Updated

A new folder is added each week with that week's assignment, following the same structure: notebook + dataset reference + brief README summarizing objective, techniques used, and insights.
