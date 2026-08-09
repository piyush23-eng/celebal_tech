# Week 1 — Basic Data Exploration & Cleaning using Pandas

## 🎯 Objective

Learn Python basics and perform basic data exploration and cleaning using Pandas on a raw shopping/e-commerce dataset — the foundation for every cleaning step used in later weeks (Week 5's PySpark cleaning and Week 8's `clean_orders()`/`clean_products()` build directly on these same ideas).

## 🛠️ Steps Covered

1. **Load** the raw CSV dataset into a Pandas DataFrame
2. **Explore** the data — `.head()` / `.tail()`, `.shape`, `.columns`, `.dtypes` to understand structure and types before touching anything
3. **Handle missing values** — identify which columns have nulls and decide, column by column, whether to fill or drop
4. **Basic operations** — filter rows on conditions, select specific columns
5. **Remove duplicate records** using `.drop_duplicates()`
6. **Create a derived column** — `total_amount = price * quantity`
7. **Export** the cleaned dataset as a new CSV file

## 📈 Key Insights

<!-- Fill in your actual numbers from the notebook output, e.g.:
- Dataset had N rows, M columns before cleaning
- X rows had missing values in [column], handled by [fill/drop strategy]
- Y duplicate rows removed
-->

## 📁 Output

- Jupyter Notebook (`.ipynb`) with all steps executed
- Cleaned CSV file
- Brief summary of findings

## 🔧 Tech Used

Python, Pandas, Jupyter Notebook / Google Colab
