# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
records=[]
for fn,source in [('nbv_annual.html','https://www.nbvplc.com/annual.html'),('nbv_financial.html','https://www.nbvplc.com/financial.html')]:
 soup=BeautifulSoup(PROJECT_ROOT / fn.read_text(errors='ignore'),'html.parser')
 for a in soup.find_all('a',href=True):
  title=' '.join(a.get_text(' ',strip=True).split()); href=urljoin(source,a['href']); low=(title+' '+href).lower()
  if '.pdf' not in href.lower():continue
  if not any(k in low for k in ['annual report','annual reports','financial statement','financial results','un-audited results','audited results','six months','quarter']):continue
  if any(k in low for k in ['agm','proxy','resolution','notice','circular','dividend']):continue
  records.append({'title':title,'url':href,'filename':href.rsplit('/',1)[-1],'source_page':source})
seen=set();out=[]
for r in records:
 if r['url'] not in seen:out.append(r);seen.add(r['url'])
with open(str(PROJECT_ROOT / 'nbv_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename','source_page']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
