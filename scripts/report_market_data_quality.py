from pathlib import Path
import os, sqlite3, json
BASE=Path(os.environ.get('NORP_ROOT', Path(__file__).resolve().parents[1]))
DB=BASE/'data'/'indexes'/'nse_reports_archive.sqlite'
con=sqlite3.connect(DB)
q=lambda sql: con.execute(sql).fetchall()
report={
 'datasets':q('select count(*) from market_dataset')[0][0],
 'import_files':q('select count(*) from market_import_file')[0][0],
 'observations':q('select count(*) from market_observation')[0][0],
 'sector_rows':q('select count(*) from market_sector_classification')[0][0],
 'anomalies':q('select count(*) from market_data_anomaly')[0][0],
 'anomaly_types':q('select anomaly_type,count(*) from market_data_anomaly group by anomaly_type order by count(*) desc'),
 'rights_status':q('select rights_status,count(*) from market_dataset group by rights_status'),
 'dataset_rows':q('select original_filename,release_period,source_archive,source_relative_path,rights_status,row_count from vw_market_dataset_catalog order by original_filename'),
 'observation_date_bounds':q('select min(trading_date),max(trading_date),count(distinct trading_date) from market_observation'),
 'tickers':q('select count(distinct ticker) from market_observation where ticker is not null and trim(ticker)<>""')[0][0],
 'duplicate_content_groups':q('select count(*) from (select source_file_sha256 from market_dataset group by source_file_sha256 having count(*)>1)')[0][0],
}
con.close()
lines=['# Attached NSE Market-Data Integration Quality Report','', '**Input basis:** attached user-supplied archive, extracted for passive inspection; permitted source datasets only are included in the NORP integration.','', '## Imported scope','', '| Layer | Count |','| --- | ---: |',f"| Original CSV datasets preserved | {report['datasets']} |",f"| Imported files | {report['import_files']} |",f"| Price observations | {report['observations']} |",f"| Sector rows | {report['sector_rows']} |",f"| Review anomalies | {report['anomalies']} |",f"| Distinct tickers in observations | {report['tickers']} |",f"| Duplicate checksum groups preserved | {report['duplicate_content_groups']} |",'', '## License and provenance','', '| Rights status | Datasets |','| --- | ---: |']
lines += [f'| {a} | {b} |' for a,b in report['rights_status']]
lines += ['', 'The attached source records identify all 32 imported CSV datasets as Mendeley Data releases under CC BY 4.0 and provide release URLs and attribution for the 2007–2026 coverage. Duplicate files from separate source packages are preserved with distinct archive provenance and checksums.', '', '## Anomaly interpretation','', '| Anomaly type | Rows |','| --- | ---: |']
lines += [f'| {a} | {b} |' for a,b in report['anomaly_types']]
lines += ['', 'Anomalies are review flags, not dropped records. The importer preserves every original row in the raw CSV copies and retains `raw_row_json` for anomaly rows; it does not impute missing prices, coerce unparsed dates into guesses, or remove apparent data-quality issues. Duplicate files from separate archives remain separate datasets with archive and relative-path provenance.', '', '## Coverage','', f"Observed date bounds are `{report['observation_date_bounds'][0][0]}` to `{report['observation_date_bounds'][0][1]}` across {report['observation_date_bounds'][0][2]} distinct parsed trading dates. The source files include 2007–2026 releases, with 2026 identified as January–June in the source naming and attribution notes. Exact row-level use should respect each dataset’s `release_period` and original filename.", '', '## Privacy boundary','', 'The NORP repository contains the permitted market-data extracts and source attribution metadata only. Only the permitted source datasets and attribution metadata are included in the public repository.']
(BASE/'docs'/'market_data_quality_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(BASE/'data'/'market_data'/'market_data_quality.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in {'dataset_rows'}},indent=2,default=str))
