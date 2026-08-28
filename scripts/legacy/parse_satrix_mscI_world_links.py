# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
records=[
 ('2025','Satrix MSCI World Feeder ETF Annual Financial Statements 2025.pdf','https://satrix.co.za/media/92364'),
 ('2024','Satrix MSCI World Feeder Portfolio Annual Financial Statements 2024.pdf','https://satrix.co.za/media/90866'),
 ('2023','Satrix MSCI World Feeder Portfolio Annual Financial Statements 2023.pdf','https://satrix.co.za/media/88196'),
 ('2022','Satrix MSCI World ETF Annual Financial Statements 2022.pdf','https://satrix.co.za/media/76632'),
 ('2020','Satrix MSCI World Feeder ETF Annual Financial Statements 2020.pdf','https://satrix.co.za/media/50977'),
 ('2019','Satrix MSCI World Feeder ETF Annual Financial Statements 2019.pdf','https://satrix.co.za/media/40165'),
 ('2018','Satrix MSCI World Feeder ETF Annual Financial Statements 2018.pdf','https://satrix.co.za/media/30891'),
 ('2017','Satrix MSCI World Feeder ETF Annual Financial Statements 2017.pdf','https://satrix.co.za/media/30816'),
 ('2016','Satrix MSCI World Feeder ETF Annual Financial Statements 2016.pdf','https://satrix.co.za/media/22204'),
]
out=[]
for y,title,url in records:out.append({'title':title,'year':y,'url':url,'filename':url.rsplit('/',1)[-1]+'.pdf','source_page':'https://satrix.co.za/products/product-details?id=33'})
with open(str(PROJECT_ROOT / 'satrix_msci_world_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','year','url','filename','source_page']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
