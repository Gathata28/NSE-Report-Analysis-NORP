# Real-Source Import Configurations

These configurations prove the canonical `scripts/norp_import.py` pattern against eight existing NORP source indexes. They are deterministic because the inputs are archived CSV indexes under `data/indexes/`; no live collection is performed by this proof run.

From the repository root, run:

```bash
for config in examples/migration_configs/*.json; do
  python scripts/norp_import.py --config "$config"
done
```

The generated canonical outputs are written to `data/migrated_indexes/` and use the `REPORT_FIELDS` schema defined in `scripts/norp_engine.py`.

| Configuration | Output rows validated |
|---|---:|
| `bk_group.json` | 56 |
| `family.json` | 20 |
| `kplc.json` | 14 |
| `limuru.json` | 1 |
| `ncba.json` | 9 |
| `newgold.json` | 6 |
| `nse_annual.json` | 7 |
| `unga.json` | 26 |
| **Total** | **139** |

The proof run also added regression coverage for `direct_url` and `source_page_url` aliases and for hyphenated integrated-report titles. The output records preserve source provenance and do not claim that linked PDFs have been independently re-verified by this import-only step.
