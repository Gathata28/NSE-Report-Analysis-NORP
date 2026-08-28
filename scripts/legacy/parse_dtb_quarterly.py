# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'dtbk.dtbafrica.com_quarterly-financial-reports_1787818738296.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
 url=a['href']
 if '.pdf' not in url.lower():continue
 p=a;title=''
 for _ in range(7):
  p=p.parent
  if p is None:break
  t=' '.join(p.get_text(' ',strip=True).split())
  if re.search(r'(20\d{2}).*(Quarter|Half|Full Year)',t,re.I) and len(t)<300:
   title=t;break
 if not title:title=' '.join(a.get_text(' ',strip=True).split()) or url.rsplit('/',1)[-1]
 if re.search(r'(20\d{2}).*(quarter|half|full year)',title,re.I):
  rows.append({'title':title,'url':url})
seen=set();out=[]
for r in rows:
 if r['url'] not in seen:seen.add(r['url']);out.append(r)
with open(str(PROJECT_ROOT / 'dtb_quarterly_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(out)
print('rows',len(out));[print(r['title'],'|',r['url']) for r in out]
