# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

from pathlib import Path
import sqlite3, json
BASE=Path(__import__('os').environ.get('NORP_ROOT', Path(__file__).resolve().parents[1]))
ROOT=BASE/'data'/'indexes' if (BASE/'data'/'indexes'/'nse_reports_archive.sqlite').exists() else BASE
DB=ROOT/'nse_reports_archive.sqlite'
con=sqlite3.connect(DB)
q=lambda sql: con.execute(sql).fetchall()
reports=q('select count(*) from report')[0][0]
issuers=q('select count(*) from issuer')[0][0]
files=q('select count(*) from report_file')[0][0]
texts=q('select count(*) from report_text')[0][0]
qual=q('select count(*) from report_qualitative')[0][0]
facts=q('select count(*) from report_fact')[0][0]
gaps=q('select count(*) from coverage_gap')[0][0]
valid=q('select verification_status,count(*) from report_validation group by verification_status')
methods=q('select extraction_method,count(*) from report_text group by extraction_method')
con.close()
lines=['# NSE Relational Database Quality Report','', '**Reference date:** 27 August 2026','', '## Scope', '', 'This SQLite database imports the complete 1,761-row normalized report index and its provenance fields. It adds structured issuer, report, source, validation, coverage-gap, local-file, raw-text, qualitative, and quantitative-fact tables. The database is analysis-ready but is not represented as error-free or as a complete extraction of every PDF: most URLs were not downloaded, and only two local scanned PDFs were OCR-processed.', '', '## Counts', '', '| Layer | Rows |', '| --- | ---: |', f'| Issuers | {issuers} |', f'| Reports | {reports} |', f'| Report sources | {reports} |', f'| Validation records | {reports} |', f'| Verified local files | {files} |', f'| OCR/text pages | {texts} |', f'| Raw qualitative page records | {qual} |', f'| Candidate quantitative facts | {facts} |', f'| Open coverage gaps | {gaps} |', '', '## Validation and extraction interpretation', '', '| Validation status | Rows |', '| --- | ---: |']
lines += [f'| {a} | {b} |' for a,b in valid]
lines += ['', '| Extraction method | Rows |','| --- | ---: |']
lines += [f'| {a} | {b} |' for a,b in methods]
lines += ['', 'The 251 quantitative rows are conservative line-level candidates from OCR text. Their numeric field is intentionally `NULL`, their original OCR line is retained in `value_text`, and every row is marked `needs_review` / `unresolved`. They are not audited financial metrics and must not be used as validated numeric data without manual review against the PDF page and table context.', '', 'The 52 qualitative rows preserve page-level OCR text as `unclassified_ocr_text` with `needs_review` / `unresolved` status. This preserves narrative evidence without asserting an automated topic classification.', '', '## Safe use', '', 'Use `vw_report_catalog` for report and source provenance, `vw_periodic_core_reports` for core periodic records, `vw_fact_panel` for review-flagged candidate facts, and `vw_data_quality_flags` for unresolved periods, weak sources, and validation issues. Always retain the original source URL and page locator when promoting a fact to a validated analysis field.', '', '## Limitations', '', 'The current-NSE coverage audit represents 65 of 66 current rows; TRFC / TRIFIC Green USD I-REIT remains an explicit gap. The historical universe has 64 preliminary candidates, including secondary-only discovery leads; it is not an authoritative all-time delisting register. Source-link HTTP validation is a bounded representative sample rather than a full crawl. Absence from a current list is not treated as proof of delisting, suspension, absorption, or insolvency.']
((BASE/'docs'/'nse_database_quality_report.md') if (BASE/'docs').exists() else (ROOT/'nse_database_quality_report.md')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'reports':reports,'issuers':issuers,'local_files':files,'text_pages':texts,'qualitative_rows':qual,'candidate_facts':facts,'open_gaps':gaps},indent=2))
