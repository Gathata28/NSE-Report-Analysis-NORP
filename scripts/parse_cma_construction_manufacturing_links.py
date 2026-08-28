# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
records=[
 {'issuer':'ARM Cement PLC','ticker':'ARM','title':'Athi River Mining Limited Annual Report and Financial Statements 2005','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/CONSTRUCTION%20AND%20ALLIED/Athi%20River%20Mining/2005.pdf'},
 {'issuer':'ARM Cement PLC','ticker':'ARM','title':'Athi River Mining Limited Annual Report and Financial Statements 2007','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/CONSTRUCTION%20AND%20ALLIED/Athi%20River%20Mining/2007.pdf'},
 {'issuer':'Mumias Sugar PLC','ticker':'MSC','title':'Mumias Sugar Company Limited Annual Report and Financial Statements 1996','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/MANUFACTURING%20AND%20ALLIED/Mumias%20Sugar%20Co.%20Ltd/1996.pdf'},
 {'issuer':'Mumias Sugar PLC','ticker':'MSC','title':'Mumias Sugar Company Limited Annual Report and Financial Statements 1997','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/MANUFACTURING%20AND%20ALLIED/Mumias%20Sugar%20Co.%20Ltd/1997.pdf'},
 {'issuer':'Mumias Sugar PLC','ticker':'MSC','title':'Mumias Sugar Company Limited Annual Report and Financial Statements 2007/2008','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/MANUFACTURING%20AND%20ALLIED/Mumias%20Sugar%20Co.%20Ltd/2007.pdf'},
 {'issuer':'Mumias Sugar PLC','ticker':'MSC','title':'Mumias Sugar Company Limited Annual Report and Financial Statements 2014','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/MANUFACTURING%20AND%20ALLIED/Mumias%20Sugar%20Co.%20Ltd/2014.pdf'},
 {'issuer':'Mumias Sugar PLC','ticker':'MSC','title':'Mumias Sugar Company Limited Audited Financial Statements for the period ended 30 June 2016','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/monday/halfyear/MANUFACTURING%20AND%20ALLIED/Mumias%20sugar/FY%202016.pdf'},
 {'issuer':'E.A. Portland Cement PLC','ticker':'PORT','title':'East African Portland Cement Company Annual Report and Financial Statements 2013','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/NSE%20Listed%20companies%20Annual%20Reports/CONSTRUCTION%20AND%20ALLIED/E.A%20Portland%20Cement/2013.pdf'},
 {'issuer':'E.A. Portland Cement PLC','ticker':'PORT','title':'East African Portland Cement Company Announcement of Audited Results FY 2015','url':'https://www.cmarcp.or.ke/joomlatools-files/docman-files/monday/halfyear/CONSTRUCTION%20AND%20ALLIED/EAST%20AFRICAN%20PORTLAND/full%20year/FY%202015.pdf'},
]
for r in records:r.update(filename=r['url'].rsplit('/',1)[-1],source_page='https://www.cmarcp.or.ke/',source_tier='CMA/regulator fallback')
with open(str(PROJECT_ROOT / 'cma_construction_manufacturing_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['issuer','ticker','title','url','filename','source_page','source_tier']);w.writeheader();w.writerows(records)
print('records',len(records))
for r in records:print(r)
