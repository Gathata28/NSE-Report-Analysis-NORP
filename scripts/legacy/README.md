# Retired Legacy Importers

These scripts are retained for historical provenance and output comparison only. They were migrated to the config-driven `scripts/norp_import.py` workflow and are no longer part of the active collection path.

| Retired script | Replacement configuration |
|---|---|
| `parse_bk_group_links.py` | `examples/migration_configs/bk_group.json` |
| `parse_family_annual_links.py` | `examples/migration_configs/family.json` |
| `parse_kplc_links.py` | `examples/migration_configs/kplc.json` |
| `parse_limuru_nse_fallback_links.py` | `examples/migration_configs/limuru.json` |
| `parse_ncba_quarterly.py` | `examples/migration_configs/ncba.json` |
| `parse_newgold_api_links.py` | `examples/migration_configs/newgold.json` |
| `parse_nse_issuer_annual_links.py` | `examples/migration_configs/nse_annual.json` |
| `parse_unga_links.py` | `examples/migration_configs/unga.json` |

Do not extend these scripts for new collection work. Keep them only until the corresponding canonical output has been compared and the provenance record is no longer dependent on their implementation details.

## Batch one additions

The following ten importers were validated against their archived source CSVs, normalized through `norp_import.py`, and retired from the active scripts directory:

| Retired script | Replacement configuration | Validated records |
|---|---|---:|
| `add_absa_to_index.py` | `examples/migration_configs/absa.json` | 105 |
| `add_bat_to_index.py` | `examples/migration_configs/bat.json` | 33 |
| `add_boc_to_index.py` | `examples/migration_configs/boc.json` | 13 |
| `add_britam_to_index.py` | `examples/migration_configs/britam.json` | 15 |
| `add_carbacid_to_index.py` | `examples/migration_configs/carbacid.json` | 1 |
| `add_cargen_to_index.py` | `examples/migration_configs/cargen.json` | 25 |
| `add_centum_annual_to_index.py` | `examples/migration_configs/centum.json` | 22 |
| `add_cic_to_index.py` | `examples/migration_configs/cic.json` | 38 |
| `add_crown_to_index.py` | `examples/migration_configs/crown.json` | 19 |
| `add_eabl_no_network.py` | `examples/migration_configs/eabl.json` | 68 |

The batch produced **339 canonical records**. `parse_transcentury_links.py` remains active and is not part of this retired set.

## Batch two additions

| Retired script | Replacement configuration | Validated records |
|---|---|---:|
| `add_longhorn_to_index.py` | `examples/migration_configs/longhorn.json` | 32 |
| `add_nbk_to_index.py` | `examples/migration_configs/nbk.json` | 64 |
| `add_scb_to_index.py` | `examples/migration_configs/scb.json` | 81 |
| `add_stanbic_to_index.py` | `examples/migration_configs/stanbic.json` | 138 |
| `add_total_to_index.py` | `examples/migration_configs/total.json` | 22 |
| `parse_sameer_links.py` | `examples/migration_configs/sameer.json` | 40 |
| `parse_home_afrika_links.py` | `examples/migration_configs/home_afrika.json` | 19 |
| `parse_express_links.py` | `examples/migration_configs/express.json` | 7 |
| `parse_jubilee_links.py` | `examples/migration_configs/jubilee.json` | 14 |
| `parse_kakuzi_links.py` | `examples/migration_configs/kakuzi.json` | 24 |

Batch two produced **441 canonical records**.

## Batch three additions

| Retired script | Replacement configuration | Validated records |
|---|---|---:|
| `parse_eaagads_links.py` | `examples/migration_configs/eaagads.json` | 7 |
| `parse_flametree_links.py` | `examples/migration_configs/flametree.json` | 11 |
| `parse_hfcb_links.py` | `examples/migration_configs/hfcb.json` | 80 |
| `parse_im_links.py` | `examples/migration_configs/im.json` | 90 |
| `parse_laptrust_links.py` | `examples/migration_configs/laptrust.json` | 6 |
| `parse_nbv_links.py` | `examples/migration_configs/nbv.json` | 22 |
| `parse_olympia_links.py` | `examples/migration_configs/olympia.json` | 9 |
| `parse_sanlam_allianz_links.py` | `examples/migration_configs/sanlam_allianz.json` | 18 |
| `parse_satrix_mscI_world_links.py` | `examples/migration_configs/satrix_msci_world.json` | 9 |
| `parse_sgl_links.py` | `examples/migration_configs/sgl.json` | 30 |

Batch three produced **282 canonical records**. All batch-two and batch-three source files were deterministic archived indexes; no live network collection was performed for these batches.

## Automatic archived-index migration

An additional **59 archived report-link indexes** were successfully normalized through `norp_import.py`, producing **1,434 records** under `data/migrated_indexes/batch_auto_*.csv`. Their generated configurations are under `examples/migration_configs/` and retain the issuer, ticker, source page, source tier, and archived input path derived from the canonical normalized index.

The following utilities remain specialized rather than being falsely represented as one-issuer report importers: `add_historical_nbk.py` (historical index transformation), `parse_africanfinancials.py` (aggregator discovery), `parse_cdsc_listed_companies.py` (issuer-universe discovery), `parse_nse_sites.py` and `parse_nse_universe.py` (NSE universe discovery), `parse_transcentury_links.py` (nested live detail-page discovery with an empty archived report index), and `parse_williamson_links.py` (multi-issuer source, now split into the Williamson and Kapchorua configurations). These remain retained for specialized provenance and should not be used as parallel active collection paths without dedicated fixtures and review.
