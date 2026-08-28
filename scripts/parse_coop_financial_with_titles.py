# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.co-opbank.co.ke_investor-relations_financial-statements__1787815857152.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
    href=a['href']
    if not href.lower().endswith('.pdf'): continue
    parent=a
    title=''
    for _ in range(6):
        parent=parent.parent
        if parent is None: break
        h=parent.find(['h2','h3','h4'])
        if h:
            title=re.sub(r'\s+',' ',h.get_text(' ',strip=True)); break
    if title and 'financial' in title.lower():
        rows.append({'title':title,'url':href})
with open(str(PROJECT_ROOT / 'coop_financial_titled.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(rows)
print('rows',len(rows))
for r in rows:print(r['title'],'|',r['url'])
