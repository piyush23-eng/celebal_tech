# E-Commerce Order Analytics System

Intern mini-project — Celebal Technologies (CEI Program), Week 8.
Skills: Python, SQL, Problem Solving.

Builds a small but complete analytics pipeline for a messy e-commerce dataset:
generate synthetic (intentionally dirty) data → clean it → load it into
SQLite → run 16 analytical SQL queries → serve results through a CLI report
tool. Everything below actually runs; nothing here is a stub.

## Why it's built this way

The brief says the raw data "comes from multiple sources and is messy." I
treated that literally instead of generating clean data and sprinkling a
few nulls on top afterward — dirty values are injected *during* generation
(wrong date formats, blank customer_ids, messy product names, bad emails,
a handful of orphan `order_items`), and the cleaning step has to actually
detect and handle each one. The data quality report in `reports/` is the
proof: it lists exact counts of what was found and fixed, not just a
"cleaning ran successfully" message.

One deliberate design call, on the hint in the brief ("how will you ensure
`order_id` in `order_items` actually exists in the orders table?"): orders
are generated first, and `order_items` sample their `order_id` from that
existing pool — so referential integrity holds by construction for ~99.9%
of rows. Then I inject exactly 6 orphan rows on purpose, so
`check_referential_integrity()` has something real to catch and I could
verify it actually works, instead of writing a function that trivially
returns an empty list on data that was never going to break it.

## Project structure

```
ecommerce-order-analytics/
├── src/
│   ├── generate_data.py     # Part 1: synthetic data with intentional issues
│   ├── clean_data.py        # Part 2: clean_orders, clean_products,
│   │                         #         validate_emails, check_referential_integrity
│   ├── load_to_sqlite.py    # loads cleaned CSVs into data/ecommerce.db
│   ├── run_queries.py       # executes every query in sql/analysis.sql,
│   │                         # saves results + a summary
│   └── cli_report.py        # Part 4: stdlib-only CLI report tool
├── sql/
│   └── analysis.sql         # Part 3: all 16 queries, basic → advanced
├── tests/
│   └── test_edge_cases.py   # Part 5: 4 edge-case tests
├── data/
│   ├── raw/                 # generated, messy CSVs
│   ├── cleaned/              # cleaned CSVs
│   └── ecommerce.db          # SQLite database
├── reports/
│   └── data_quality_report.md
├── query_results/            # CSV + summary for each of the 16 queries
├── requirements.txt
└── run_pipeline.sh           # one command, runs everything in order
```

## Running it

```bash
pip install -r requirements.txt
bash run_pipeline.sh
```

That single script runs, in order: data generation → cleaning → SQLite
load → all 16 SQL queries → the edge-case test suite. Takes a few seconds.

To run a single stage on its own:

```bash
python3 src/generate_data.py
python3 src/clean_data.py
python3 src/load_to_sqlite.py
python3 src/run_queries.py
python3 tests/test_edge_cases.py -v
```

### CLI report tool (Part 4)

```bash
python3 src/cli_report.py --type monthly --start 2024-06-01 --end 2024-06-30
```

Omit any flag and it will prompt for it interactively. Uses only `sqlite3`,
`argparse`, and `datetime` from the standard library, per the brief's
"no external libraries except sqlite3" constraint. Output:

```
============================================================
  MONTHLY REPORT   |   2024-06-01 to 2024-06-30
============================================================
  Total Orders       : 50
  Total Revenue      : Rs 6,843,703.11
  Unique Customers   : 45

  Top 3 Products:
    1. Sequi Laptops Ele25                 Rs 431,153.47
    2. Maxime Haircare Bea141              Rs 330,631.91
    3. Eveniet Non-Fiction Boo97            Rs 295,853.43

  vs. Previous Period (2024-05-02 to 2024-05-31):
    Orders    :     53  ->      50   (-5.66%)
    Revenue   : Rs 9,092,750.22  ->  Rs 6,843,703.11   (-24.73%)
    Customers :     46  ->      45   (-2.17%)
============================================================
```

The "previous period" is computed as a same-length window immediately
before the requested range — a 7-day request compares against the
preceding 7 days, a full month against the preceding full-length window.

## Data model

```
customers (customer_id PK)
    │
    ▼ 1:N
orders (order_id PK, customer_id FK, order_date, status, region_code)
    │
    ▼ 1:N
order_items (item_id PK, order_id FK, product_id FK, quantity, unit_price, discount_percent)
    ▲
    │ N:1
products (product_id PK, product_name, category, subcategory, cost_price)
```

`revenue` is computed consistently everywhere in this project as:

```
revenue = quantity * unit_price * (1 - discount_percent / 100)
```

Negative `quantity` (returns) is deliberately **included** in this formula
rather than filtered out — a return should reduce revenue, not be invisible
to it. That's also why `unit_price` is intentionally a markup over each
product's `cost_price` (not equal to it) in the generated data: it gives
every category and product a plausible, non-uniform margin instead of a
uniform round number.

## Notable implementation choices in the SQL (Part 3)

- **Q3 (month-wise, last 12 months)** is anchored to `MAX(order_date)` in
  the table rather than the system clock — otherwise a historical/demo
  dataset with no orders in the actual current month would return nothing.
- **Q6 / Q16** rely on `quantity < 0` as the return signal and
  `product_id < product_id` (self-join) to avoid double-counting A-B/B-A
  pairs, exactly as specified.
- **Q9 (LAG)** computes `avg_days_gap` per customer in a separate CTE first,
  then joins it back — a single-pass `AVG() OVER (...)` window can't easily
  express "average of *this customer's* gaps" alongside the per-row gap in
  the same SELECT without repeating the whole `LAG` expression, so I split
  it into two CTEs for clarity over cleverness.
- **Q15 (cohort retention)** computes `month_offset` from calendar year/month
  arithmetic rather than raw day differences, since "month 1" for a customer
  who registered on the 28th shouldn't require exactly 30 days to have
  passed.

## Data quality issues intentionally injected (and caught)

| Issue | Where | Rate | Result on this run |
|---|---|---|---|
| Missing `customer_id` | orders.csv | 5% | 114 flagged, kept |
| Wrong date format (`DD-MM-YYYY`) | orders.csv | 5% | 99 detected & normalized |
| Negative quantity (returns) | order_items.csv | 3% | 209 flagged as `is_return` |
| Invalid email (no `@` / no domain) | customers.csv | 2% | 9 detected |
| Messy product names (spacing/case) | products.csv | ~25% | 37 normalized |
| Orphan `order_items` (bad `order_id`) | order_items.csv | fixed count (6) | 6/6 caught & removed |

Full breakdown in `reports/data_quality_report.md`, regenerated fresh
every time `clean_data.py` runs.

## Note on categories

Products use exactly the 4 categories named in the brief — Electronics,
Clothing, Home, Books — nothing added.

## Honest scope notes

- Money values are in a generic currency unit (₹-style formatting used in
  the CLI tool since I built this on an INR locale, but nothing is
  currency-specific in the schema or SQL — swap the formatting if needed).
- Faker's `en_IN` locale is used for names/emails, which is why customer
  emails and names skew Indian — didn't seem worth genericizing given who
  this is for.
- Part 4's "no external libraries except sqlite3" constraint means that
  tool alone doesn't use pandas, even though the rest of the project does.
- Cleaning is non-destructive by design: rows with fixable issues are
  fixed, rows with unfixable issues (missing FK, bad email) are **flagged**,
  not deleted — except the 6 orphan `order_items`, which are removed
  because an item that can't be attributed to any order can't be
  attributed to anything downstream either.
