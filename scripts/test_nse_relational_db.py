# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

from pathlib import Path
import hashlib, sqlite3, json
BASE=Path(__import__('os').environ.get('NORP_ROOT', Path(__file__).resolve().parents[1]))
ROOT=BASE/'data'/'indexes' if (BASE/'data'/'indexes'/'nse_reports_archive.sqlite').exists() else BASE
DB=ROOT/'nse_reports_archive.sqlite'
con=sqlite3.connect(DB)
con.execute('PRAGMA foreign_keys=ON')
checks={}
checks['foreign_key_violations']=con.execute('PRAGMA foreign_key_check').fetchall()
checks['reports']=con.execute('SELECT COUNT(*) FROM report').fetchone()[0]
checks['sources']=con.execute('SELECT COUNT(*) FROM report_source').fetchone()[0]
checks['validations']=con.execute('SELECT COUNT(*) FROM report_validation').fetchone()[0]
checks['local_files']=con.execute('SELECT COUNT(*) FROM report_file').fetchone()[0]
checks['qualitative_rows']=con.execute('SELECT COUNT(*) FROM report_qualitative').fetchone()[0]
checks['fact_rows']=con.execute('SELECT COUNT(*) FROM report_fact').fetchone()[0]
checks['open_gaps']=con.execute("SELECT COUNT(*) FROM coverage_gap WHERE status='open'").fetchone()[0]
checks['duplicate_report_ids']=con.execute('SELECT COUNT(*) FROM (SELECT report_id FROM report GROUP BY report_id HAVING COUNT(*)>1)').fetchone()[0]
checks['orphan_sources']=con.execute('SELECT COUNT(*) FROM report_source s LEFT JOIN report r ON r.report_id=s.report_id WHERE r.report_id IS NULL').fetchone()[0]
checks['orphan_validations']=con.execute('SELECT COUNT(*) FROM report_validation v LEFT JOIN report r ON r.report_id=v.report_id WHERE r.report_id IS NULL').fetchone()[0]
checks['view_catalog_rows']=con.execute('SELECT COUNT(*) FROM vw_report_catalog').fetchone()[0]
checks['view_core_rows']=con.execute('SELECT COUNT(*) FROM vw_periodic_core_reports').fetchone()[0]
checks['unresolved_fact_rows']=con.execute("SELECT COUNT(*) FROM report_fact WHERE quality_status='needs_review'").fetchone()[0]
checks['ocr_pages']=con.execute("SELECT COUNT(*) FROM report_text WHERE extraction_method='tesseract-ocr'").fetchone()[0]
checks['failed_checks']=[k for k,v in checks.items() if (isinstance(v,int) and v<0) or (isinstance(v,list) and v)]
print(json.dumps(checks,indent=2))
if checks['failed_checks'] or checks['duplicate_report_ids'] or checks['orphan_sources'] or checks['orphan_validations']:
    raise SystemExit(1)
con.close()
