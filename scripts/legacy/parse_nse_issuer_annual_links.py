# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'nse_annual_archive.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.nse.co.ke/annual-reports/',a['href']);fn=href.rsplit('/',1)[-1]
 if '.pdf' not in href.lower():continue
 low=(fn+' '+href).lower();text=' '.join(a.get_text(' ',strip=True).split())
 if any(k in low for k in ['strategy','agm','aide','pricelist','market-data']):continue
 if not any(k in low for k in ['annual','integrated','financial','report']):continue
 title=text or fn
 if href not in {r['url'] for r in out}:out.append({'title':title,'url':href})
with open(str(PROJECT_ROOT / 'nse_issuer_annual_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
