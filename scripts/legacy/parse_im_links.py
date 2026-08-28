# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.imbankgroup.com_financial-results-annual-reports-and-investor-presentation__1787817521042.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
    url=urljoin('https://www.imbankgroup.com/financial-results-annual-reports-and-investor-presentation/',a['href'])
    if '.pdf' not in url.lower():continue
    parent=a; text=''
    for _ in range(5):
        parent=parent.parent
        if parent is None:break
        t=' '.join(parent.get_text(' ',strip=True).split())
        if t and len(t)<500 and ('I&M' in t or 'IM ' in t or 'Financial' in t or 'Report' in t): text=t
    if not text:text=' '.join(a.get_text(' ',strip=True).split())
    # use URL filename as fallback; omit obvious non-report materials
    fname=url.rsplit('/',1)[-1]
    if not any(k in (text+' '+fname).lower() for k in ['financial','report','results','annual','hy','half','q1','q3','q2','investor']):continue
    rows.append({'title':text or fname,'url':url})
# dedupe exact URLs, retain most specific title
seen=set();out=[]
for r in rows:
    if r['url'] not in seen:seen.add(r['url']);out.append(r)
with open(str(PROJECT_ROOT / 'im_report_links.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(out)
print('rows',len(out))
for r in out:print(r['title'],'|',r['url'])
