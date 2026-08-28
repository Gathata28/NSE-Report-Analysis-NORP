# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'bamburigroup.com_bamburi-unaudited-half-year-group-financial-statements-fy-2025__1787826947821.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://bamburigroup.com/bamburi-unaudited-half-year-group-financial-statements-fy-2025/',a['href'])
 text=' '.join(a.get_text(' ',strip=True).split())
 if '.pdf' not in href.lower():continue
 if text.lower() in ('download report (pdf)','download pdf','download report') or 'financial' in (text+' '+href).lower():
  out.append({'title':'Bamburi Unaudited Half Year Group Financial Statements FY 2025','url':href,'filename':href.rsplit('/',1)[-1]})
seen=set();clean=[]
for r in out:
 if r['url'] not in seen:clean.append(r);seen.add(r['url'])
with open(str(PROJECT_ROOT / 'bamburi_h1_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(clean)
print('records',len(clean))
for r in clean:print(r)
