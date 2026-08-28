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
