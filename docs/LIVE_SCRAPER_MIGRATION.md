# Live Scraper Migration

## Scope

The KPLC report-link collector was migrated from the retired legacy implementation to `scripts/collect_kplc_live.py`. The collector uses `norp_engine.fetch_with_retry()` with the issuer-website retry tier, a reusable requests session, bounded timeout behavior, verified TLS defaults, and a per-host semaphore.

## Verification

The collector was run against the public KPLC investor-relations page:

`https://www.kplc.co.ke/investor-relations/`

The live run completed successfully and wrote `data/migrated_indexes/kplc_live.csv` containing **11 canonical report-link records**. The first implementation matched an unrelated E-Mobility conference PDF because it used the generic word `report`; that false-positive path was removed by requiring financial-report evidence in nearby card text and report-specific terms. The corrected live run passed the full 11-test suite and Python compilation.

The output is a link-collection result, not a claim that every PDF was independently downloaded and content-verified during this migration phase. PDF verification remains governed by the archive validation workflow and source provenance requirements.
