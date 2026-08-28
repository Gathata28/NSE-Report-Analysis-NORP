# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re,requests
from bs4 import BeautifulSoup
pages=[
('KenGen Integrated Annual Report & Financial Statement 2025','https://www.kengen.co.ke/download/kengen-integrated-annual-report-financial-statement-2025/'),
('KenGen Integrated Annual Report & Financial Statement 2024','https://www.kengen.co.ke/download/kengen-integrated-annual-report-financial-statement-2024/'),
('2023 Integrated Annual Report & Financial Statement','https://www.kengen.co.ke/download/2023-integrated-annual-report-financial-statement/'),
('Integrated Annual Report & Financial Statements','https://www.kengen.co.ke/download/integrated-annual-report-financial-statements-4/')]
s=requests.Session();s.headers.update({'User-Agent':'Mozilla/5.0'})
rows=[]
for title,page in pages:
    r=s.get(page,timeout=40); soup=BeautifulSoup(r.text,'html.parser'); a=soup.select_one('a[data-downloadurl]')
    if a:
        url=a.get('data-downloadurl')
        rows.append({'title':title,'page_url':page,'download_url':url,'status':r.status_code})
        print(title,'|',page,'|',url,'|',r.status_code)
    else: print('NO LINK',title,r.status_code)
with open(str(PROJECT_ROOT / 'kengen_report_links.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['title','page_url','download_url','status']);w.writeheader();w.writerows(rows)
