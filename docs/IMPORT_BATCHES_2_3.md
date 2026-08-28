# Import Migration Batches 2 and 3

## Summary

Batches 2 and 3 continued the config-driven migration against archived report-link indexes. Each output was produced by `scripts/norp_import.py`, then validated with the full pytest suite, Python compilation, database integrity checks, report-index quality checks, and market-data quality checks before the corresponding legacy parser was retired.

| Batch | Configurations | Canonical records | Legacy scripts retired |
|---|---:|---:|---:|
| 2 | 10 | 441 | 10 |
| 3 | 10 | 282 | 10 |
| **Combined** | **20** | **723** | **20** |

## Batch two

Batch two covered Longhorn, National Bank of Kenya, Standard Chartered Bank Kenya, Stanbic Holdings, TotalEnergies Marketing Kenya, Sameer Africa, Home Afrika, Express Kenya, Jubilee Holdings, and Kakuzi. Its outputs are named `data/migrated_indexes/batch2_*.csv` and its configurations are named `examples/migration_configs/{longhorn,nbk,scb,stanbic,total,sameer,home_afrika,express,jubilee,kakuzi}.json`.

## Batch three

Batch three covered Eaagads, Flame Tree, HF Group, I&M Group, LAPTRUST Imara I-REIT, Nairobi Business Ventures, Olympia Capital, Sanlam Allianz, Satrix MSCI World Feeder ETF, and Standard Group. Its outputs are named `data/migrated_indexes/batch3_*.csv` and its configurations are named `examples/migration_configs/{eaagads,flametree,hfcb,im,laptrust,nbv,olympia,sanlam_allianz,satrix_msci_world,sgl}.json`.

## Reproduction

From the repository root, run:

```bash
for batch in 2 3; do
  for config in examples/migration_configs/*.json; do
    case "$config" in
      *batch2*|*batch3*) python scripts/norp_import.py --config "$config" ;;
    esac
done
done
```

The explicit per-batch output paths in each configuration are the authoritative reproduction mapping. The archived source indexes preserve original source-page and download-link provenance; these migrations do not claim independent live PDF verification.

## Retirement

The replaced legacy files are retained under `scripts/legacy/` for historical provenance and output comparison only. The remaining active legacy scripts include discovery-only utilities, NSE/CMA-specific parsers, and report-link collectors not yet covered by a deterministic configuration. They must be handled in later source-pattern batches rather than being silently classified as migrated.

## Batch four and automatic coverage

The multi-issuer Williamson source was split without data loss into two issuer-specific indexes. `williamson.json` produced 14 Williamson Tea records and `kapchorua.json` produced 14 Kapchorua records, for **28 additional canonical records**.

A deterministic provenance join then generated configurations for **59 additional archived report-link indexes**, all of which ran successfully and produced **1,434 canonical records**. These configurations include historical NSE/CMA fallback sources, issuer annual and periodic archives, ETF records, and structured indexes whose first URL matched an existing canonical provenance record. Their outputs use the `batch_auto_*.csv` naming convention.

The only legacy utilities not represented by a one-issuer configuration are documented as specialized exceptions in `scripts/legacy/README.md`: issuer-universe discovery, aggregator discovery, historical-index transformation, and the TransCentury nested live-detail collector whose archived report index is empty. They are not counted as silently migrated report-link importers.
