# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.kplc.co.ke_annual-reports_1787817689228.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
    url=urljoin('https://www.kplc.co.ke/annual-reports',a['href'])
    if not url.lower().endswith('.pdf'):continue
    title=''
    p=a
    for _ in range(7):
        p=p.parent
        if p is None:break
        txt=' '.join(p.get_text(' ',strip=True).split())
        if any(k in txt.lower() for k in ['annual report','financial results','financial statements','financials','trading results']) and len(txt)<700:
            title=txt;break
    if not title:title=' '.join(a.get_text(' ',strip=True).split())
    low=(title+' '+url).lower()
    if any(k in low for k in ['annual report','financial results','financial statements','financials','trading results']):
        rows.append({'title':title,'url':url})
seen=set();out=[]
for r in rows:
    if r['url'] not in seen:seen.add(r['url']);out.append(r)
with open(str(PROJECT_ROOT / 'kplc_report_links.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(out)
print('rows',len(out))
for r in out:print(r['title'],'|',r['url'])
