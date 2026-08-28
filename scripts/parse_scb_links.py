# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.sc.com_ke_investor-relations__1787817395785.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
    url=urljoin('https://www.sc.com/ke/investor-relations/',a['href'])
    if '.pdf' not in url.lower():continue
    text=' '.join(a.get_text(' ',strip=True).split())
    parent=a;near=''
    for _ in range(4):
        parent=parent.parent
        if parent is None:break
        t=' '.join(parent.get_text(' ',strip=True).split())
        if len(t)>0 and len(t)<500:near=t
    label=text or near
    low=(label+' '+url).lower()
    if not any(k in low for k in ['annual','financial','results','statement','abridged','q1','q2','q3','q4','h1','half']):continue
    if any(k in low for k in ['agm','proxy','polling','charter','governance','policy','sustainability','question']):continue
    rows.append({'title':label,'url':url})
with open(str(PROJECT_ROOT / 'scb_report_links.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(rows)
print('rows',len(rows))
for r in rows:print(r['title'],'|',r['url'])
