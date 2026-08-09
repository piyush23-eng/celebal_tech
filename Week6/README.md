# Week 6 — Spark Architecture: Lazy Evaluation, DAGs & File Format Tradeoffs

## 🎯 Objective

Understand how Spark actually executes a job under the hood — building on Week 5's hands-on PySpark cleaning work with the conceptual model of *why* Spark behaves the way it does, and reason about storage format tradeoffs for analytical workloads.

## 🧠 Topics Covered

1. **Transformations vs. actions** — why Spark defers execution (`.filter()`, `.select()`, `.groupBy()` are transformations; `.show()`, `.count()`, `.collect()` are actions that actually trigger a job)
2. **Lazy evaluation** — how deferring execution lets Spark's Catalyst optimizer plan the most efficient physical execution before any computation runs, instead of executing each step immediately and naively
3. **DAG (Directed Acyclic Graph) construction** — how Spark builds a lineage graph of transformations, and how that lineage is what makes fault tolerance possible (a lost partition can be recomputed from the DAG instead of needing a full re-run)
4. **Predicate pushdown** — filtering data as close to the storage layer as possible (e.g. inside a Parquet reader) instead of loading everything into memory and filtering afterward
5. **CSV vs. Parquet** — columnar vs. row-based storage, compression efficiency, schema enforcement, and the read/write performance gap between the two for analytical (read-heavy) workloads

## 📈 Key Insights

<!-- Fill in your actual findings, e.g.:
- Benchmark: Parquet read was Nx faster than CSV for [operation]
- File size comparison: CSV vs Parquet for the same dataset
- Where predicate pushdown measurably reduced data scanned
-->

## 📁 Output

- Jupyter Notebook (`.ipynb`)
- Brief summary of findings

## 🔧 Tech Used

PySpark, Parquet, CSV
