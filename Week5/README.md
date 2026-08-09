# Week 5 — Spark Fundamentals: Data Cleaning & Aggregation

## 🎯 Objective

Understand Spark's in-memory architecture over traditional MapReduce, and apply PySpark DataFrames for cleaning, filtering, and aggregating a real dataset — the hands-on counterpart to Week 6's conceptual deep-dive into *why* Spark executes the way it does.

## 📦 Dataset

[E-Commerce Transactions Dataset](https://www.kaggle.com/datasets/smayanj/e-commerce-transactions-dataset) (Kaggle, 50K rows)

## 🛠️ Steps Covered

1. MapReduce limitations vs. Spark's in-memory computing (conceptual)
2. DataFrame immutability and its effect on cleaning pipelines (conceptual)
3. Deduplication using `dropDuplicates()`
4. Null detection across all columns + handling via `.na.drop()` / `.na.fill()`
5. Conditional filtering (age range + category/subscription-tier equivalents)
6. GroupBy aggregations using `.agg()` — min, max, mean, sum
7. Shuffle process and wide vs. narrow transformations (conceptual)
8. Multi-format timestamp casting via `try_to_timestamp` + `coalesce`
9. Risks of `inferSchema=True` on inconsistent date formats (conceptual)
10. Final chained pipeline: dedup → fill nulls → aggregate revenue by category

## 📈 Key Insights

- Removed **13,846 duplicate rows** out of 50,000
- **Books** was the top-revenue category (~₹23.2L)
- Achieved **0 failed timestamp casts** using explicit multi-format parsing instead of relying on `inferSchema`

## 📁 Output

- Jupyter Notebook (`.ipynb`) with executed outputs
- Brief summary of findings

## 🔧 Tech Used

PySpark (local mode)
