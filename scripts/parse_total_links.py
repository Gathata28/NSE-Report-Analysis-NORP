# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re,html as htmlmod
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'total_financials.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=htmlmod.unescape(urljoin('https://totalenergies.ke/about-us/shareholder-information/financials',a['href']))
 title=' '.join(a.get_text(' ',strip=True).split());low=(title+' '+href).lower()
 if any(k in low for k in ['agm','poll','notice','question','proxy']):continue
 if not any(k in low for k in ['annual','financial statement','financials statement','full-year','full year','half year','half-year','un-audited']):continue
 if not ('.pdf' in href.lower() or 'wedia' in href.lower()):continue
 if href not in {x['url'] for x in out}:out.append({'title':title,'url':href})
with open(str(PROJECT_ROOT / 'total_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
