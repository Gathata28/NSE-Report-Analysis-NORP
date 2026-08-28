# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.stanbicbank.co.ke_kenya_personal_about-us_investor-relations_1787818536136.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
 url=urljoin('https://www.stanbicbank.co.ke/kenya/personal/about-us/investor-relations',a['href'])
 if '.pdf' not in url.lower():continue
 text=' '.join(a.get_text(' ',strip=True).split())
 low=(text+' '+url).lower()
 if not any(k in low for k in ['annual','financial','result','statement','full year','half year','h1','q1','q2','q3','q4']):continue
 if any(k in low for k in ['governance','proxy','polling','mandate','policy','sustainability','reporttosociety','agm','board &','committee']):continue
 if not text:text=url.rsplit('/',1)[-1]
 if url not in {r['url'] for r in rows}:rows.append({'title':text,'url':url})
with open(str(PROJECT_ROOT / 'stanbic_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(rows)
print('rows',len(rows));[print(r['title'],'|',r['url']) for r in rows]
