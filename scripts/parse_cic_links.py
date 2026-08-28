# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'cic_ir.html')).read_text(errors='ignore'),'html.parser')
rows=[]
for tr in soup.find_all('tr'):
    a=tr.find('a',href=True)
    if not a or '.pdf' not in a['href'].lower():continue
    title=' '.join(tr.get_text(' ',strip=True).split())
    url=urljoin('https://www.cicinsurancegroup.com/investor-relations/',a['href'])
    low=(title+' '+url).lower()
    if not any(k in low for k in ['annual','financial','result','statement','half','quarter','h1','q1','q2','q3','q4']):continue
    if any(k in low for k in ['agm','governance','proxy','policy','circular','poll','question','appointment','bonus','profit warning','shareholder notice']):continue
    if url not in {r['url'] for r in rows}:rows.append({'title':title,'url':url})
# Also collect standalone report links outside tables if the title/URL is clearly a financial report.
for a in soup.find_all('a',href=True):
    url=urljoin('https://www.cicinsurancegroup.com/investor-relations/',a['href'])
    if '.pdf' not in url.lower():continue
    title=' '.join(a.get_text(' ',strip=True).split())
    low=(title+' '+url).lower()
    if any(k in low for k in ['annual','financial','result','statement','half','quarter','h1','q1','q2','q3','q4']) and not any(k in low for k in ['agm','governance','proxy','policy','circular','poll','question','appointment','bonus','profit warning','shareholder notice']):
        if url not in {r['url'] for r in rows}:rows.append({'title':title or url.rsplit('/',1)[-1],'url':url})
with open(str(PROJECT_ROOT / 'cic_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(rows)
print('rows',len(rows));[print(r['title'],'|',r['url']) for r in rows]
