# Public-Release Verification

**Project:** Nairobi Securities Exchange Report Analysis Project (NORP)

This checklist is the maintainer’s final review before publishing a repository update or a versioned GitHub Release. It is written for contributors who may not have worked on the archive before.

## Repository and data state

The public repository is organized into `docs/`, `scripts/`, `schema/`, `data/`, and `examples/`. Root release files include `README.md`, `CITATION.cff`, `CONTRIBUTING.md`, `LICENSE`, `requirements.txt`, and `pyproject.toml`.

The current SQLite snapshot contains 1,761 report records, 189 issuer identity rows, 1,761 report sources, and 1,761 report validations. The market-data layer contains 32 datasets, 381,400 price observations, and 577 sector-classification rows. The database is source-preserving infrastructure: it retains source confidence, validation status, original text, page locators, unresolved periods, anomaly flags, and review candidates. It is not claimed to be free of error, and it is not investment advice.

## Required local checks

Run these commands from the repository root:

```bash
pytest -q
python -m compileall -q scripts tests
python scripts/test_nse_relational_db.py
python scripts/test_report_index_quality.py
python scripts/report_market_data_quality.py
```

The public filtered downloader should also pass a dry-run smoke test:

```bash
python scripts/download_reports.py \
  --output-dir /tmp/norp-download-preview \
  --sector BANKING \
  --year-from 2020 \
  --year-to 2025 \
  --limit 5 \
  --dry-run
```

## Security checks

The active workflows use custom advanced CodeQL, enforced Bandit, token-free Semgrep Community Edition, OSV-Scanner, and the NORP integrity checks. GitHub Actions references are pinned to immutable commit SHAs. Do not add credentials, environment-specific absolute paths, private upstream project markers, or new `verify=False` network requests.

The downloader must continue to record 403 responses and unresolved landing pages. It must not bypass authentication, CAPTCHA, robots controls, TLS verification, or anti-bot protections.

## Package checks

Build and inspect both standard Python distribution formats:

```bash
python -m pip install --upgrade build twine
python -m build --outdir /tmp/norp-dist
python -m twine check /tmp/norp-dist/*
```

Install the wheel into a temporary virtual environment and verify both commands:

```bash
python -m venv /tmp/norp-package-venv
/tmp/norp-package-venv/bin/python -m pip install /tmp/norp-dist/*.whl
/tmp/norp-package-venv/bin/norp-download-reports --help
/tmp/norp-package-venv/bin/norp-import --help
```

The package intentionally does not embed the approximately 70 MB SQLite database. Users download a matching database Release asset and pass it with `--database` when running an installed command outside a repository checkout.

## Release-artifact checks

Large database and index snapshots are staged outside the working tree:

```bash
python scripts/bundle_outputs.py \
  --version 0.2.0 \
  --output-dir /tmp/norp-release-0.2.0
```

Review the generated release manifest and `SHA256SUMS_0.2.0.txt`. Each artifact must have a stable GitHub Release URL, a 64-character SHA-256 checksum, byte size, release label, and license metadata. Validate the manifest against `docs/release_manifest.schema.json` when a JSON Schema validator is available.

To publish the first or next release, create and push a tag in the form `vMAJOR.MINOR.PATCH`:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The `.github/workflows/release.yml` workflow builds the wheel and source distribution, stages the SQLite and CSV-index assets outside Git history, fills `docs/release_notes_template.md`, and publishes the resulting files to GitHub Releases. Inspect the published release and verify one downloaded asset against its checksum file.

## Large-file policy

The checked-in SQLite snapshot is retained for immediate offline analysis, but new large ZIPs, PDFs, and database snapshots must not be added casually to normal Git history. Versioned snapshots belong in GitHub Releases under the policy documented in `docs/large_file_management.md`.

## Final maintainer sign-off

Before publication, confirm that the working tree is clean, the intended commit is on `main`, the package version and tag agree, the Release manifest points to the intended tag, the licenses are accurate, and the README links to all user-facing workflows. Record any known source gaps or blocked downloads in the release notes rather than presenting the archive as complete or error-free.
