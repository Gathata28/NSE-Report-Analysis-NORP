# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'bamburigroup.com_bamburi-cement-investor-relations_annual-reports__1787826766242.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://bamburigroup.com/bamburi-cement-investor-relations/annual-reports/',a['href'])
 title=' '.join((a.get('aria-label') or a.get('title') or a.get_text(' ',strip=True) or '').split())
 parent=a.parent
 context=' '.join(parent.get_text(' ',strip=True).split()) if parent else ''
 low=(href+' '+title+' '+context).lower()
 if any(k in low for k in ['agm','proxy','polling','notice','governance','policy','shareholder','board','sustainability']):continue
 if not any(k in low for k in ['annual report','financial report','financial statement','report','results','half-year','half year','interim']):continue
 if href.startswith('mailto:') or href.endswith('#'):continue
 if href not in [r['url'] for r in out]:out.append({'title':title or context[:200],'url':href,'filename':href.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'bamburi_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
