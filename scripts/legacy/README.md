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
