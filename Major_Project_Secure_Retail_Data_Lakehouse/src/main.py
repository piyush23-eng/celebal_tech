"""
main.py
-------
Orchestrates the full Bronze -> Silver -> Gold batch pipeline end to end.

Each stage is wrapped so a failure produces a clear, specific message
and a non-zero exit code -- important for a "batch pipeline" since in
production this exit code is what a scheduler (cron/ADF/Airflow) would
check to decide whether to alert someone.

Usage:
    python src/main.py                # uses existing data/raw_transactions.csv
    python src/main.py --regen-data   # regenerates synthetic raw data first
    python src/main.py -v             # verbose (DEBUG-level) logging
"""

import argparse
import logging
import os
import sys

import bronze_layer
import dashboard
import data_generator
import gold_layer
import silver_layer
from config import BRONZE_PATH, BRONZE_QUARANTINE_PATH, GOLD_DIR, RAW_PATH, SILVER_PATH
from exceptions import LakehousePipelineError

logger = logging.getLogger("lakehouse.main")


def parse_args():
    parser = argparse.ArgumentParser(description="Secure Retail Data Lakehouse pipeline")
    parser.add_argument("--regen-data", action="store_true", help="regenerate synthetic raw source data")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable DEBUG-level logging")
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    try:
        if args.regen_data or not os.path.exists(RAW_PATH):
            logger.info("=== Simulating raw operational extract ===")
            data_generator.main()

        logger.info("=== BRONZE: raw ingestion ===")
        bronze_layer.ingest(RAW_PATH, BRONZE_PATH, BRONZE_QUARANTINE_PATH)

        logger.info("=== SILVER: PII/PCI masking, tokenization, binning ===")
        silver_layer.transform(BRONZE_PATH, SILVER_PATH)

        logger.info("=== GOLD: business analytics ===")
        gold_layer.run(SILVER_PATH, GOLD_DIR)
        dashboard.build_dashboard(GOLD_DIR, f"{GOLD_DIR}/gold_layer_dashboard.png")

    except LakehousePipelineError as exc:
        # Expected, specific pipeline failures (bad source file, schema
        # mismatch, every row quarantined, PII leakage guard tripped).
        # Logged as a clean one-liner, not a raw traceback, and exits
        # non-zero so a scheduler/CI step correctly reports failure.
        logger.error("Pipeline stopped: %s", exc)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001 -- deliberate final safety net
        # Anything NOT already classified above is a bug, not a data
        # problem -- log it distinctly so it's obvious this needs a code
        # fix rather than a data fix.
        logger.error("Unexpected error (this is a bug, not a data issue): %s", exc, exc_info=args.verbose)
        sys.exit(2)

    logger.info("Pipeline complete. Bronze/Silver/Gold artifacts are in their respective folders.")


if __name__ == "__main__":
    main()
