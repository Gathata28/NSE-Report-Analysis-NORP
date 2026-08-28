# Packaging and GitHub Releases

This guide explains how NORP is distributed. The Python tools are small enough to package as a wheel and source distribution. The SQLite archive and index ZIP are distributed as separate GitHub Release assets because the database is much larger than ordinary Python package files.

## For ordinary users

If you only want the downloader or importer, install the Python package from a built wheel or from PyPI when a maintainer publishes it:

```bash
python -m pip install norp-nse-report-analysis
```

If you install from a GitHub Release asset instead:

```bash
python -m pip install norp_nse_report_analysis-0.2.0-py3-none-any.whl
```

Download the matching `nse_reports_archive_<version>.sqlite` release asset and use it explicitly:

```bash
norp-download-reports \
  --database ./nse_reports_archive_0.2.0.sqlite \
  --output-dir ./downloads/kplc \
  --ticker KPLC
```

The package does not embed the 70 MB database. This keeps installation quick and lets users choose a specific archive snapshot.

## For maintainers

Create an isolated build environment and build both standard distribution formats:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade build
python -m build --outdir dist
```

Stage the large release assets outside the working tree:

```bash
python scripts/bundle_outputs.py \
  --version 0.2.0 \
  --output-dir /tmp/norp-release-0.2.0
cp dist/* /tmp/norp-release-0.2.0/
```

Review the generated `release_manifest_0.2.0.json` and `SHA256SUMS_0.2.0.txt`. The manifest must contain stable GitHub Release URLs, SHA-256 checksums, byte sizes, release labels, and license metadata. Validate the manifest against [`release_manifest.schema.json`](release_manifest.schema.json) when a JSON Schema validator is available.

Publish a release by creating and pushing a semantic version tag:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The tagged GitHub Actions workflow then builds the wheel and source distribution, stages the database and CSV-index ZIP outside the working tree, fills [`release_notes_template.md`](release_notes_template.md), and publishes all generated assets to the GitHub Release. The workflow requires the repository’s default `GITHUB_TOKEN` with `contents: write`; no personal token is stored in the repository.

## Versioning policy

Use `MAJOR.MINOR.PATCH` tags prefixed with `v`, such as `v0.2.0`. Increase the major version for incompatible CLI or database-contract changes, the minor version for backward-compatible features, and the patch version for bug fixes or documentation-only corrections that warrant a new stable asset snapshot.

## Licensing and redistribution

The MIT License applies to NORP code, schemas, and documentation. The market-data extracts retain their CC BY 4.0 attribution requirements. Report PDFs remain subject to their source issuers’ permissions and terms; the existence of a release asset does not change those terms. The release notes and manifest deliberately separate NORP software licensing from source-report licensing.

## Release checklist

Before pushing a tag, run `pytest -q`, compile the active scripts, run the relational and report-index quality gates, build the wheel and source distribution, inspect the manifest and checksums, and confirm that no large release asset is inside the Git working tree. After publication, download one asset, verify it against `SHA256SUMS_<version>.txt`, and confirm that the release notes identify the source commit.
