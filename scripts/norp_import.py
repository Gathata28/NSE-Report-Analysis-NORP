"""Config-driven NORP report-link importer."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from norp_engine import load_csv, normalize_source_records, write_index

LOGGER = logging.getLogger("norp_import")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a source CSV into a NORP report index.")
    parser.add_argument("--config", type=Path, required=True, help="JSON configuration file.")
    parser.add_argument("--dry-run", action="store_true", help="Print normalized records without writing output.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(message)s")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    required = ["issuer", "ticker", "source_page", "input_csv", "output_csv"]
    missing = [key for key in required if not config.get(key)]
    if missing:
        parser.error(f"Missing config keys: {', '.join(missing)}")
    root = args.config.resolve().parent
    input_csv = (root / config["input_csv"]).resolve()
    output_csv = (root / config["output_csv"]).resolve()
    records = normalize_source_records(
        load_csv(input_csv),
        issuer=config["issuer"], ticker=config["ticker"],
        source_page=config["source_page"], source_tier=config.get("source_tier", "Issuer website"),
    )
    existing = load_csv(output_csv) if output_csv.exists() else []
    combined = normalize_source_records(existing, issuer=config["issuer"], ticker=config["ticker"], source_page=config["source_page"], source_tier=config.get("source_tier", "Issuer website")) if existing else []
    merged = combined + [row for row in records if row["download_url"] not in {r["download_url"] for r in combined}]
    LOGGER.info("normalized=%d existing=%d merged=%d", len(records), len(existing), len(merged))
    if args.dry_run:
        print(json.dumps(merged, indent=2))
    else:
        write_index(output_csv, merged)
        LOGGER.info("wrote %s", output_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
