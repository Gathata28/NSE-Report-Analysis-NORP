"""Build versioned, checksummed artifacts for GitHub Releases."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def project_root() -> Path:
    return Path(os.environ.get("NORP_ROOT", Path(__file__).resolve().parents[1])).resolve()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_version(version: str) -> str:
    cleaned = version.strip()
    if not cleaned or any(char in cleaned for char in "/\\\0"):
        raise ValueError("version must be a non-empty release-safe label")
    return cleaned


def make_indexes_zip(root: Path, destination: Path, version: str) -> list[Path]:
    source_dirs = [root / "data" / "indexes", root / "data" / "migrated_indexes"]
    source_files = [
        path
        for directory in source_dirs
        if directory.exists()
        for path in sorted(directory.glob("*.csv"))
        if path.is_file()
    ]
    if not source_files:
        raise FileNotFoundError("No CSV indexes found for the release bundle")
    zip_path = destination / f"norp_indexes_{version}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in source_files:
            archive.write(source, source.relative_to(root).as_posix())
    return [zip_path]


def build_bundle(root: Path, output_dir: Path, version: str) -> dict[str, object]:
    version = safe_version(version)
    output_dir = output_dir.resolve()
    if output_dir.is_relative_to(root):
        raise ValueError("output_dir must be outside the project working tree")
    output_dir.mkdir(parents=True, exist_ok=True)

    database = root / "data" / "indexes" / "nse_reports_archive.sqlite"
    if not database.exists():
        raise FileNotFoundError(database)
    database_asset = output_dir / f"nse_reports_archive_{version}.sqlite"
    shutil.copyfile(database, database_asset)
    assets = [database_asset, *make_indexes_zip(root, output_dir, version)]

    release_tag = version if version.startswith("v") else f"v{version}"
    records = []
    for asset in assets:
        records.append(
            {
                "filename": asset.name,
                "stable_url": f"https://github.com/Gathata28/NSE-Report-Analysis-NORP/releases/download/{release_tag}/{asset.name}",
                "sha256": sha256(asset),
                "bytes": asset.stat().st_size,
                "release_label": version,
                "license_metadata": [
                    "MIT for NORP code, schemas, and documentation",
                    "CC BY 4.0 for licensed NSE market data; see docs/market_data_licensing.md",
                ],
            }
        )

    manifest = {
        "project": "NSE-Report-Analysis-NORP",
        "release_label": version,
        "release_tag": release_tag,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "artifact_host": "GitHub Releases",
        "artifacts": records,
        "source_policy": "Generated outside the working tree from the current checked-out repository state; not copied from Git history.",
    }
    manifest_path = output_dir / f"release_manifest_{version}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    checksums_path = output_dir / f"SHA256SUMS_{version}.txt"
    checksums_path.write_text(
        "".join(f"{record['sha256']}  {record['filename']}\n" for record in records),
        encoding="utf-8",
    )
    return {
        "manifest": str(manifest_path),
        "checksums": str(checksums_path),
        "artifacts": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage checksummed NORP GitHub Release artifacts outside the repository.")
    parser.add_argument("--version", required=True, help="Release label, such as 2026.08.28 or v2026.08.28.")
    parser.add_argument("--output-dir", type=Path, required=True, help="External staging directory, outside NORP.")
    args = parser.parse_args()
    result = build_bundle(project_root(), args.output_dir, args.version)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
