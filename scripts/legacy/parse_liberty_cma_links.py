# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
url='https://annualreport.cma.or.ke/media/INSURANCE/Liberty%20Kenya%20Holdings/documents/2022.pdf'
row={'issuer':'Liberty Kenya Holdings PLC','ticker':'LBTY','title':'Liberty Life Assurance Kenya Limited Annual Financial Statements and Reports for the year ended 31 December 2022','url':url,'filename':'2022.pdf','source_page':'https://annualreport.cma.or.ke/','source_tier':'CMA/regulator fallback'}
with open(str(PROJECT_ROOT / 'liberty_cma_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=row.keys());w.writeheader();w.writerow(row)
print('records',1);print(row)
