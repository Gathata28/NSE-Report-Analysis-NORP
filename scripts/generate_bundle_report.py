"""Generate a human-readable completion report for a NORP download bundle.

The report combines the downloader JSONL manifest with the optional extraction
JSONL manifest. It is intentionally file-based so it works before a bundle is
imported into the SQLite database and can be attached to a release ZIP.

Example::

    python scripts/generate_bundle_report.py \
        --download-manifest downloads/banking/download_manifest.jsonl \
        --extraction-manifest downloads/banking/extraction_manifest.jsonl \
        --output downloads/banking/BUNDLE_STATUS.md
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def read_jsonl(path: Path | None) -> list[dict[str, Any]]:
    """Read a JSON Lines manifest, returning an empty list for an omitted path."""
    if path is None or not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path} at line {line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Manifest row {line_number} in {path} is not an object")
        rows.append(value)
    return rows


def markdown_report(downloads: list[dict[str, Any]], extractions: list[dict[str, Any]], title: str) -> str:
    """Render bundle counts and pending work as Markdown."""
    statuses = Counter(row.get("status", "unknown") for row in downloads)
    methods = Counter(row.get("extraction_method", "unknown") for row in extractions)
    attempted = len(downloads)
    retrieved = statuses["downloaded"] + statuses["skipped_existing"]
    verified = sum(1 for row in downloads if row.get("status") in {"downloaded", "skipped_existing"} and row.get("sha256") and row.get("byte_size", 0) > 0)
    pending = sum(count for status, count in statuses.items() if status not in {"downloaded", "skipped_existing"})
    lines = [f"# {title}", "", "> Generated from NORP downloader and extraction manifests. Counts describe this bundle only; they do not claim that the full archive is complete.", "", "## Download status", "", "| Measure | Count |", "| --- | ---: |", f"| Catalog rows selected | {attempted} |", f"| Retrieved or already present | {retrieved} |", f"| Retrieved rows with checksum and size | {verified} |", f"| Pending or unsuccessful rows | {pending} |", "", "### Status breakdown", "", "| Status | Count |", "| --- | ---: |"]
    lines.extend(f"| `{status}` | {count} |" for status, count in sorted(statuses.items()))
    lines.extend(["", "## Text extraction status", "", "| Method | Count |", "| --- | ---: |"])
    lines.extend(f"| `{method}` | {count} |" for method, count in sorted(methods.items()))
    if not extractions:
        lines.extend(["| Not run | 0 |", "", "Text extraction has not been run for this bundle."])
    failed = [row for row in extractions if row.get("extraction_status") != "extracted"]
    if failed:
        lines.extend(["", "## Extraction failures", "", "| PDF | Error |", "| --- | --- |"])
        lines.extend(f"| `{row.get('pdf_path', '')}` | {row.get('error', 'unknown error')} |" for row in failed)
    lines.extend(["", "## Interpretation", "", "A downloaded PDF is not equivalent to a reviewed report. Text extracted by `pdftotext` or Tesseract is evidence for analysis, while numeric facts remain subject to manual source-page verification and the database quality status rules.", ""])
    return "\n".join(lines)


def main() -> int:
    """Generate the requested Markdown bundle report."""
    parser = argparse.ArgumentParser(description="Generate a Markdown completion report for a NORP download bundle.")
    parser.add_argument("--download-manifest", type=Path, required=True)
    parser.add_argument("--extraction-manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", default="NORP Bundle Status")
    args = parser.parse_args()
    downloads = read_jsonl(args.download_manifest)
    extractions = read_jsonl(args.extraction_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown_report(downloads, extractions, args.title), encoding="utf-8")
    print(json.dumps({"download_rows": len(downloads), "extraction_rows": len(extractions), "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
