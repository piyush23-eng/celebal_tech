#!/usr/bin/env bash
# Runs the full pipeline end to end: generate -> clean -> load -> analyze.
set -e

echo "== Step 1/4: Generating raw data ================================"
python3 src/generate_data.py

echo
echo "== Step 2/4: Cleaning data ========================================"
python3 src/clean_data.py

echo
echo "== Step 3/4: Loading into SQLite =================================="
python3 src/load_to_sqlite.py

echo
echo "== Step 4/4: Running all 16 SQL queries ==========================="
python3 src/run_queries.py

echo
echo "== Running edge case tests =========================================="
python3 tests/test_edge_cases.py

echo
echo "All done. See reports/, query_results/, and data/ecommerce.db"
