# Import Migration Batch 1

## Scope

Batch 1 validates the config-driven importer against ten additional real-source index files that were previously handled by issuer-specific `add_*` scripts. The inputs are archived source CSVs already included in NORP, so the migration is deterministic and does not make network requests.

| Issuer | Ticker | Input index | Output records |
|---|---|---|---:|
| Absa Bank Kenya PLC | ABSA | `data/indexes/absa_report_links.csv` | 105 |
| British American Tobacco Kenya PLC | BAT | `data/indexes/bat_report_links.csv` | 33 |
| BOC Kenya PLC | BOC | `data/indexes/boc_report_links.csv` | 13 |
| Britam Holdings PLC | BRIT | `data/indexes/britam_annual_links.csv` | 15 |
| Carbacid Investments PLC | CARB | `data/indexes/carbacid_report_links.csv` | 1 |
| Car & General (Kenya) PLC | CGEN | `data/indexes/cargen_report_links.csv` | 25 |
| Centum Investment Company PLC | CTUM | `data/indexes/centum_annual_report_links.csv` | 22 |
| CIC Insurance Group PLC | CIC | `data/indexes/cic_report_links.csv` | 38 |
| Crown Paints Kenya PLC | CRWN | `data/indexes/crown_report_links.csv` | 19 |
| East African Breweries PLC | EABL | `data/indexes/eabl_financial_results_links.csv` | 68 |

The batch produced **339 canonical records**. Each configuration is under `examples/migration_configs/`, and each output is under `data/migrated_indexes/`.

## Reproduction

Run the following from the repository root:

```bash
for config in absa bat boc britam carbacid cargen centum cic crown eabl; do
  python scripts/norp_import.py \
    --config "examples/migration_configs/${config}.json" \
    --log-level INFO
done
```

The importer is idempotent by download URL and the complete repository test suite must pass after the batch. The report-index quality gate continues to validate the canonical database independently of these flat-file migration outputs.

## Retirement

The corresponding ten legacy scripts were moved to `scripts/legacy/` and recorded in `scripts/legacy/README.md`. The active import path is now the shared engine plus JSON configuration. The remaining legacy scripts are tracked for later pattern-based batches; `parse_transcentury_links.py` is intentionally still active and was not silently treated as migrated.
