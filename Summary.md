# Assignment Summary — Python & Pandas Fundamentals

**Dataset:** Sample Superstore (9,994 retail order line-items, 21 columns)

## What I did
1. Loaded the CSV into Pandas and profiled it — shape, columns, dtypes, `head()`/`tail()`, `describe()`.
2. Audited data quality on the raw file: **0 missing values, 0 duplicate rows** — genuinely clean as delivered.
3. To properly exercise the assignment's cleaning steps, I simulated realistic messiness on a seeded copy
   (missing `Sales`/`Postal Code`/`Ship Mode` values, ~1% duplicate rows, inconsistent `Category` casing/whitespace)
   and then cleaned it back — validating every step against the untouched original.
4. Handled missing values with column-appropriate strategies rather than one rule for everything:
   - `Sales` → median imputed **within each Sub-Category** (price varies too much across product types for a global median)
   - `Postal Code` → rows dropped (can't be inferred, small fraction of data)
   - `Ship Mode` → filled with the mode (`Standard Class`)
5. Standardized `Category` labels (`.strip().str.title()`) and removed duplicate rows.
6. Demonstrated filtering (high-value loss-making orders, West + Consumer segment slice) and column selection.
7. Derived `Price` (unit price = `Sales / Quantity`) and `total_amount = Price * Quantity`, then **validated it
   reconstructs `Sales`** — good practice for trusting a derived field.
8. Added quick EDA (sales by category, profit by region, top 10 products) to turn the cleaning exercise into
   an actual analysis.
9. Exported the final cleaned dataset to `Superstore_cleaned.csv`.

## Key findings
- Technology and Office Supplies lead total sales; Furniture lags.
- Central region shows the weakest profit performance; West is the strongest — worth a discount-policy review,
  since high-discount, high-sales orders are frequently the loss-making ones.
- A small set of products account for a disproportionate share of top-line sales (classic 80/20 pattern).

## Files
- `delta_pandas_assignment.ipynb` — full notebook, executed with outputs
- `Superstore_cleaned.csv` — cleaned dataset with derived `Price` and `total_amount` columns
- `eda_category_region.png`, `eda_top_products.png` — exported charts
- `Summary.md` — this file
