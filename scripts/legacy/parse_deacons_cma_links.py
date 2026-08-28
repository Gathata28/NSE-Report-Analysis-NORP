# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
url='https://annualreport.cma.or.ke/media/COMMERCIAL%20AND%20SERVICES/Decons%20(East%20Africa)%20Plc/documents/2018.PDF'
records=[{'issuer':'Deacons (East Africa) PLC','ticker':'DCON','title':'Deacons (East Africa) PLC financial statements / report 2018','url':url,'filename':'2018.PDF','source_page':'https://annualreport.cma.or.ke/','source_tier':'CMA/regulator fallback'}]
with open(str(PROJECT_ROOT / 'deacons_cma_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['issuer','ticker','title','url','filename','source_page','source_tier']);w.writeheader();w.writerows(records)
print('records',len(records));print(records[0])
