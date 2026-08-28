# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'britam_annual_reports.html')).read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
 u=urljoin('https://www.britam.com/investor-relations/annual-reports',a['href'])
 if '.pdf' not in u.lower() or any(k in u.lower() for k in ['quality-policy','board-charter','stakeholders-engagement','policy']):continue
 parent=a;year='';
 for _ in range(4):
  parent=parent.parent
  if parent is None:break
  h=parent.find(['h2','h3','h4'])
  if h:
   m=re.search(r'(20\d{2})',h.get_text(' ',strip=True))
   if m:year=m.group(1);break
 if not year:
  m=re.search(r'(20\d{2})',u);year=m.group(1) if m else ''
 rows.append({'year':year,'title':f'Britam Holdings PLC Annual Report {year}','url':u})
seen=set();out=[]
for r in rows:
 if r['url'] not in seen:seen.add(r['url']);out.append(r)
with open(str(PROJECT_ROOT / 'britam_annual_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['year','title','url']);w.writeheader();w.writerows(out)
print('rows',len(out));[print(r) for r in out]
