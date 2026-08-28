# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
records=[
 {'issuer':'Uchumi Supermarkets PLC','ticker':'UCHM','title':'Uchumi Supermarkets Limited Annual Report and Financial Statements for the year ended 30 June 2013','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/monday/COMMERCIAL%20AND%20SERVICES/UCHUMI/2013.pdf'},
 {'issuer':'Uchumi Supermarkets PLC','ticker':'UCHM','title':'Uchumi Supermarkets Limited Annual Report and Financial Statements for the year ended 30 June 2015','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/monday/COMMERCIAL%20AND%20SERVICES/UCHUMI/2014-2015.pdf'},
 {'issuer':'Uchumi Supermarkets PLC','ticker':'UCHM','title':'Uchumi Supermarkets Limited Annual Report and Financial Statements for the year ended 30 June 2016','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/newdocs/COMMERCIAL%20AND%20SERVICES/UCHUMI/audited%20reports.pdf'},
 {'issuer':'Trans-Century PLC','ticker':'TCL','title':'Trans-Century Limited Annual Report and Financial Statements 2016','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/INVESTMENT/Trans-Century%20Ltd/2016.pdf'},
]
for r in records:r.update(filename=r['url'].rsplit('/',1)[-1],source_page='https://www.cmarcp.or.ke/',source_tier='CMA/regulator fallback')
with open(str(PROJECT_ROOT / 'cma_uchumi_tcl_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['issuer','ticker','title','url','filename','source_page','source_tier']);w.writeheader();w.writerows(records)
print('records',len(records))
for r in records:print(r)
