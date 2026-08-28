# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'centum_financial_results.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://centum.co.ke/centum-financial-results/',a['href']);fn=href.rsplit('/',1)[-1]
 if '.pdf' not in href.lower():continue
 low=(fn+' '+href).lower();text=' '.join(a.get_text(' ',strip=True).split())
 if any(k in low for k in ['agm','notice','proxy','sustainability','shareholder']):continue
 if not any(k in low for k in ['result','financial','interim','half','hy','fy','briefing','commentary','statement']):continue
 title=text or fn
 if href not in {x['url'] for x in out}:out.append({'title':title,'url':href,'filename':fn})
with open(str(PROJECT_ROOT / 'centum_financial_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
