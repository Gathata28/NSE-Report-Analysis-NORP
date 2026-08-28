# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'kakuzi_company_reports.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.kakuzi.co.ke/company-reports',a['href']);fn=href.rsplit('/',1)[-1]
 if '.pdf' not in href.lower():continue
 card=a.find_parent('div',class_='roww') or a.parent
 text=' '.join((card or a).get_text(' ',strip=True).split())
 low=text.lower()
 if any(k in low for k in ['governance','esg','agm','employee','human rights','sikika','proxy','polling']):continue
 if not any(k in low for k in ['annual report','interim financial statement','financial statement','financial results']):continue
 title=text.replace('Download','').strip() or fn
 # Strip surrounding date when a whole card was used.
 title=re.sub(r'\b\d{1,2}\s+[A-Z]{3}\s+20\d{2}\b','',title).strip()
 if href not in {r['url'] for r in out}:out.append({'title':title,'url':href,'filename':fn})
with open(str(PROJECT_ROOT / 'kakuzi_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
