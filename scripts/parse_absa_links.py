# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'absa_ir.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
    url=urljoin('https://www.absabank.co.ke/investor-relations/',a['href'])
    if '.pdf' not in url.lower():continue
    text=' '.join(a.get_text(' ',strip=True).split())
    parent=a;near=''
    for _ in range(5):
        parent=parent.parent
        if parent is None:break
        t=' '.join(parent.get_text(' ',strip=True).split())
        if t and len(t)<600 and any(k in t.lower() for k in ['annual','financial','results','statement']):near=t
    label=text or near or url.rsplit('/',1)[-1]
    low=(label+' '+url).lower()
    if not any(k in low for k in ['annual','financial','result','statement','abridged']):continue
    if any(k in low for k in ['proxy','agm','notice','governance','policy','sustainability','charter','shareholding','remuneration','question']):continue
    if url not in {r['url'] for r in rows}:rows.append({'title':label,'url':url})
with open(str(PROJECT_ROOT / 'absa_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(rows)
print('rows',len(rows));[print(r['title'],'|',r['url']) for r in rows]
