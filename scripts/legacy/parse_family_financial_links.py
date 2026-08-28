# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'family_financial_results.html')).read_text(errors='ignore'),'html.parser')
out=[]
for tr in soup.find_all('tr'):
 a=tr.find('a',href=True)
 if not a or '.pdf' not in a['href'].lower():continue
 href=urljoin('https://familybank.co.ke/?page_id=654',a['href'])
 title=' '.join(a.get_text(' ',strip=True).split());title=re.sub(r'\s*\([^)]*\)\s*$','',title).strip()
 low=title.lower()
 if any(k in low for k in ['tariff','remittance','newspaper','branches','notice','agm','proxy','policy']):continue
 date=' '.join(tr.find_all('td')[-1].get_text(' ',strip=True).split()) if len(tr.find_all('td'))>1 else ''
 if href not in {r['url'] for r in out}:out.append({'title':title,'publication_date':date,'url':href})
with open(str(PROJECT_ROOT / 'family_financial_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','publication_date','url']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out[:12]:print(r)
for r in out[-5:]:print(r)
