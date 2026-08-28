# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'standard_group_investors.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.standardmedia.co.ke/corporate/investors',a['href']);fn=href.rsplit('/',1)[-1]
 if '.pdf' not in href.lower():continue
 anchor=' '.join(a.get_text(' ',strip=True).split());low=(anchor+' '+fn).lower()
 if any(k in low for k in ['agm','annual general meeting','annual_general_meeting','proxy','poll','resolution','board','director','governance','charter','policy','whistle','warning','waiver','rights','cma','court','articles','code of ethics','question','appointment','resignation']):continue
 if not any(k in low for k in ['annual','financial','result','interim','half','audited','report','publication']):continue
 title=anchor if anchor.lower() not in ('download','download pdf','view pdf','+') else re.sub(r'[_-]+',' ',fn.rsplit('?',1)[0].replace('.pdf','')).strip()
 if href not in {r['url'] for r in out}:out.append({'title':title,'url':href,'filename':fn})
with open(str(PROJECT_ROOT / 'sgl_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
