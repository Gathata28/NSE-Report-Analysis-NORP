# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'longhorn_reports.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.longhornpublishers.com/investor-relations/reports/',a['href'])
 if '.pdf' not in href.lower():continue
 card=a.find_parent(['article','li','div'])
 text=' '.join((card or a).get_text(' ',strip=True).split())
 low=text.lower()
 if not any(k in low for k in ['annual report','half year','interim report','full year','financial']):continue
 if any(k in low for k in ['policy','agm','proxy','notice','governance','shareholder']):continue
 # Use the file path when card text is contaminated or missing, but keep the displayed title where available.
 title=' '.join(a.get_text(' ',strip=True).split()) or text
 if not title or title.lower() in ('download','view pdf','pdf'):title=href.rsplit('/',1)[-1]
 if href not in {r['url'] for r in out}:out.append({'title':title,'url':href})
with open(str(PROJECT_ROOT / 'longhorn_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
