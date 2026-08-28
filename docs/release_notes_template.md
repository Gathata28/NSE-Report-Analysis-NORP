# NORP {{TAG}}

This release was built from commit [`{{COMMIT}}`](https://github.com/Gathata28/NSE-Report-Analysis-NORP/commit/{{COMMIT}}).

## What is included

The release contains the pip-installable NORP downloader and importer, the source distribution and wheel, the versioned SQLite archive snapshot, the CSV-index ZIP, the release manifest, and SHA-256 checksums.

## Install the Python tools

```bash
python -m pip install norp-nse-report-analysis=={{VERSION}}
```

The large SQLite archive is distributed separately as a release asset. Download it when using the installed command outside a cloned repository, then pass its path with `--database`:

```bash
norp-download-reports \
  --database ./nse_reports_archive_{{VERSION}}.sqlite \
  --output-dir ./downloads/example \
  --ticker KPLC \
  --year-from 2020 \
  --year-to 2025
```

## Verify the assets

Use `SHA256SUMS_{{VERSION}}.txt` to verify downloaded release files before analysis or redistribution. The JSON release manifest records each stable asset URL, byte size, checksum, release label, and applicable license metadata.

## Licensing

NORP code, schemas, and documentation are released under the MIT License. Licensed NSE market-data content retains its CC BY 4.0 attribution requirements. Report PDFs remain subject to the source issuer’s terms and are not automatically relicensed by NORP.

## Reproducibility

The database and index assets were generated from the repository state identified above. The release workflow stages large artifacts outside the Git working tree so they do not inflate repository history.
