# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
records=[
 {'title':'Eveready East Africa Limited Annual Report & Financial Statements for the year ended 30 September 2010','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/MANUFACTURING%20AND%20ALLIED/Eveready%20East%20Africa%20Ltd/2010.pdf'},
 {'title':'Eveready East Africa Limited 2015 Final Results','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/halfyearstatement/MANUFACTURING%20AND%20ALLIED/EVEREADY/EEAL%202015%20finalResults.pdf'},
 {'title':'Eveready East Africa Limited Annual Report and Financial Statements 2016','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/monday/MANUFACTURING%20AND%20ALLIED/EVEREADY/2016.pdf'},
]
for r in records:r.update(filename=r['url'].rsplit('/',1)[-1],source_page='https://www.cmarcp.or.ke/',source_tier='CMA/regulator fallback')
with open(str(PROJECT_ROOT / 'eveready_cma_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename','source_page','source_tier']);w.writeheader();w.writerows(records)
print('records',len(records))
for r in records:print(r)
