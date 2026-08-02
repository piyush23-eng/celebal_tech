# Delta Lake MERGE Implementation — Short Explanation (Superstore Dataset)

**Objective:** Perform incremental data processing using Delta Lake.

## Dataset
`Sample - Superstore.csv` — 9,994 real retail order line-items, 21 columns. Since this is a static
snapshot file, it's split 85/15 to create a genuine incremental scenario:
- **`master`** (8,495 rows) — treated as the existing, already-loaded Delta table.
- **`holdout_pool`** (1,499 rows) — treated as orders not yet in the system; a subset later becomes
  the "new orders" in the incremental batch.

## What was done
1. Loaded `master` into a **Delta table** using `deltalake` (delta-rs) — the native Python implementation
   of the Delta Lake open table format (same protocol Databricks/PySpark's `DeltaTable` speaks).
2. Audited for nulls/duplicates — genuinely **0 of either** in this file as delivered. The cleaning step
   (`dropna().drop_duplicates()`) was still run explicitly rather than skipped, to prove the pipeline
   handles it.
3. Built an incremental batch of **725 rows**:
   - **425 order corrections** — 5% of existing orders sampled and given an adjusted `Discount` (+0.05)
     with `Profit` recalculated, simulating a retroactive pricing/return correction.
   - **300 new orders** — pulled from the holdout pool, representing orders that just came in.
4. Ran a single `MERGE`: `when_matched_update_all()` + `when_not_matched_insert_all()`.
5. Validated the result:
   - Final table: **8,795 rows** (8,495 + 300, exactly as expected — corrections replaced rows in place,
     they didn't duplicate them)
   - **0 duplicate `Row_ID`s** after merge
   - Profit on the corrected orders moved from **$15,113.30 → $26,724.45** (net **+$11,611.15**),
     confirming the update half of the merge genuinely changed values, not just the insert half
6. Displayed the final table and Delta's transaction history (`dt.history()`), showing the initial write
   and the merge as two separate, auditable versions of the table.

## Why MERGE, not a manual join-and-overwrite
Retailers routinely need to apply after-the-fact corrections (returns, disputed charges, pricing errors)
to historical orders while new orders keep arriving. A manual pattern — read the whole table, join the new
batch in memory, overwrite everything — isn't atomic (a crash mid-write can leave the table half-updated)
and rewrites the entire table on every load. Delta's `MERGE` figures out exactly which rows change and
commits the whole operation as one ACID transaction, which is what makes it suitable for a real
incremental/correction pipeline instead of a full reload every time.
