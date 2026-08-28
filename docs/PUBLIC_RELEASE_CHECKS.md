# Public-Release Verification

**Release target:** NORP repository structure

The repository was generated into `docs/`, `scripts/`, `schema/`, `data/`, and `examples/`. Root release files include `README.md`, `CITATION.cff`, `CONTRIBUTING.md`, `LICENSE`, `requirements.txt`, and `.gitignore`.

All 132 public Python scripts compile successfully. The public script tree contains no `/home/ubuntu`, `/home/`, sandbox-specific, or credential-pattern references after sanitization. The core database builder, integrity test, and quality-report generator run from the repository root without a `NORP_ROOT` override and resolve the database under `data/indexes/`.

The SQLite build imports 1,761 reports, 189 issuer identities, 1,761 sources, 1,761 validation records, two verified local files, 52 OCR pages, 52 raw qualitative page records, 251 review-flagged candidate facts, and one open current-universe gap. Integrity tests report zero foreign-key violations, zero duplicate report IDs, zero orphan source records, zero orphan validation records, and all analysis views execute successfully.

The repository is not claimed to be free of wrong data. It preserves source confidence, validation status, original text, page locators, unresolved periods, and review flags. Secondary materials are explicitly labeled as discovery-only, and the historical issuer universe remains preliminary.
