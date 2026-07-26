Week 6 — Spark Architecture & PySpark Data Processing
PySpark assignment covering core Spark architecture concepts alongside a hands-on read → transform → filter → write pipeline, with a focus on comparing CSV and Parquet storage formats.
Objective
Understand Spark architecture (Driver, Cluster Manager, Executors) and execution modes; learn Lazy Evaluation and the Lineage Graph (DAG); read, transform, and filter data efficiently; and compare CSV vs Parquet performance using real Spark execution plans.
Dataset
E-Commerce Transactions Dataset (Kaggle, 50K rows)
Columns: Transaction_ID, User_Name, Age, Country, Product_Category, Purchase_Amount, Payment_Method, Transaction_Date
Steps Covered
Spark architecture — roles of Driver, Cluster Manager, and Executor
Lazy Evaluation and how it optimizes chained transformations via the DAG
Reading CSV with header + inferSchema options
CSV (row-based) vs Parquet (columnar) storage and performance tradeoffs
Column selection + filtering (select(), filter())
Renaming columns and explicit type casting (withColumnRenamed, .cast())
Lineage Graph (DAG) and fault tolerance via partition recomputation
Compound filtering with AND conditions
Predicate Pushdown in Parquet — proven directly via .explain(True) physical plan output, not just described in theory
Derived columns using withColumn() (tax calculation)
Transformations vs Actions — lazy plan-building vs triggered execution
End-to-end pipeline: Parquet read → null filter → CSV write
Client Mode vs Cluster Mode deployment
Compound filtering with OR conditions
Why .show(n) is safe at scale while .collect() risks crashing the Driver
Key Insights
Verified Predicate Pushdown directly from Spark's physical execution plan — PushedFilters confirmed Spark skips irrelevant Parquet row-groups before loading data into memory
Parquet consistently outperformed CSV on filter speed across repeated averaged runs (e.g. ~0.27s vs ~0.36s for an identical filter)
Two results that look like errors at first glance are actually correct given the data: an AND-filter on Purchase_Amount > 1000 returns 0 rows because this dataset caps at 999.98, and a null-filter on User_Name is a no-op because the dataset has zero nulls in that column — both are genuine data-quality observations, not bugs
Output
Jupyter Notebook (.ipynb) with executed outputs, Spark execution plan proof, and a brief summary tying results back to theory.
