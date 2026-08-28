# NSE Reports Archive — Collection Summary

**As of:** 27 August 2026 (runtime reference date; EAT context)

## Basis

This working archive indexes publicly exposed annual, semi-annual, quarterly, and other periodic-results materials for current and historical/candidate Nairobi Securities Exchange issuers. Each indexed row preserves the issuer, ticker, taxonomy, report-year label, document subtype, webpage title, source page URL, direct download URL, source tier, and publication-date field where available. Filing or upload date is not substituted for the fiscal reporting period.

The source hierarchy is issuer investor-relations/report pages, issuer-controlled CDNs and public APIs first; official NSE and CMA regulator/exchange records are retained as explicit fallbacks. Secondary indexes were used for discovery only and are not presented as primary evidence. A document is not promoted to a periodic report merely because it is a prospectus, corporate-action notice, presentation, or general disclosure.

## Current archive state

| Artifact | Latest state |
| --- | ---: |
| Master indexed records | 1,761 |
| Issuer identities represented in master | 68 |
| Normalized core reports/statements | 1,052 |
| Normalized related materials | 709 |
| Current NSE universe denominator | 66 rows |
| Current rows with at least one indexed report record | 65 |
| Current rows without an indexed financial-report record | 1 |
| Bounded representative validation sample | 212 records |
| Sample HTTP 206 responses | 161 |
| Sample HTTP 200 responses | 33 |
| Sample HTTP errors | 11 |
| Sample HTTP 403 responses | 5 |
| Sample HTTP 404 responses | 3 |
| Corpus-wide downloaded/checksummed status | Not claimed |

The representative validation sample is not a full-corpus crawl. A 200/206 PDF response in the sample is positive evidence for that sampled URL; an error, 403, 404, or timeout is not a verified download. Most remaining indexed rows are issuer-linked and pending or untested. The normalized field `with_local_checksum` remains zero after reconstruction because older local manifests use legacy record IDs; this does not prove that no older local files exist.

## Current-universe gaps

The one current NSE row without an indexed financial-report record is **TRFC / TRIFIC Green USD I-REIT**. This is a coverage gap, not a delisting conclusion. The official NSE listed-companies page continues to enumerate the entry as of the collection date: <https://www.nse.co.ke/listed-companies/>. The official NSE financial-results page was also checked in a bounded pass without a matching report entry: <https://www.nse.co.ke/financial-results/>.

E.A. Cables’ legacy issuer archive was documented as inaccessible because of a MySQL database error and HTTPS certificate problems; its 2025 half-year result was subsequently indexed from the official NSE announcements archive. Kurwitu Ventures was resolved with an exact 2020 NSE annual financial-statements PDF. AMAC is represented cautiously through predecessor-name Kenya Orchards reports because AMAC’s official site states it was formerly Kenya Orchards Ltd. Shri Krishana Overseas was resolved through an exact 2025 NSE financial-statements PDF. TRIFIC’s prospectus remains excluded from the requested periodic-report taxonomy.

## Historical universe

The historical universe remains preliminary rather than an authoritative all-time delisted-issuer register. It currently contains 64 named candidates, including 56 matches to the current NSE-derived table and eight candidates absent from the current 66-row page. Absence from the current page is not treated as proof of delisting, suspension, absorption, or insolvency; explicit exit-event evidence is still required.

Homeboyz Entertainment is now represented by two issuer-first-party records from its official investor center: the unaudited half-year results for the period ended 30 June 2025 and the audited results announcement for the year ended December 2024. The source page is <https://homeboyz.co.ke/investor-relations>. AMAC is additionally represented by two explicitly labeled predecessor-name records for Kenya Orchards 2007 and 2020, supported by AMAC’s official predecessor-name statement at <https://amacplc.com/>.

Kenya Orchards is now represented by two CMA-hosted annual reports: the report and financial statements for the year ended 31 December 2007 and the report and financial statements for the year ended 31 December 2020. Hutchings Biemer, A. Baumann, CMC Holdings, Rea Vipingo, Atlas Development & Support Services, and Stanlib Fahari I-REIT are retained as secondary-only historical/discovery leads; no primary NSE/CMA listing or exit notice was located in this pass, so their status is not asserted as confirmed. The exact direct links and downloaded-file checksums are in `downloaded_files_manifest.csv`; the local PDFs are under `kenya_orchards/`. The CMA sources are <https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/MANUFACTURING%20AND%20ALLIED/Kenya%20Orchards%20Ltd/2007.pdf> and <https://annualreport.cma.or.ke/media/MANUFACTURING%20AND%20ALLIED/Kenya%20Orchards/documents/2020.PDF>.

## Workbook and reproducibility

`nse_reports_archive_index.xlsx` contains Readme, Report Index, Issuer Coverage, Validation Sample, Historical Universe, and Gap Disclosures sheets. It uses a consistent Arial-based layout, hyperlinks, and no formulas; the latest ZIP/XML integrity check found no corruption, formulas, or common Excel error markers. The canonical rebuild path is `rebuild_master_from_sources.py`, followed by normalization, bounded validation, validation merge, workbook generation, and current-coverage refresh. Legacy appenders should not be used.

## Confidence and limitation statement

Confidence is highest for exact titles and links exposed on issuer pages, issuer-controlled APIs/CDNs, or exact regulator PDFs. Confidence is lower for fallback links whose hosts are slow, anti-bot protected, or unavailable at validation time. The archive is analysis-ready and source-verifiable at the indexed-link level, but it is not a claim that every report ever published by every current or former NSE issuer has been found, downloaded, or permanently mirrored.

This is source research and archive work, not personalized investment advice.
