# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
html=Path(str(PROJECT_ROOT / 'crown_about.html')).read_text(errors='ignore')
soup=BeautifulSoup(html,'html.parser')
out=[]
for a in soup.find_all('a',href=True):
    href=urljoin('https://www.crownpaints.co.ke/about?tab=report#report',a['href'])
    if '.pdf' not in href.lower():continue
    card=a.find_parent(['div','article','li'])
    text=' '.join((card or a).get_text(' ',strip=True).split())
    low=(text+' '+href).lower()
    if not any(k in low for k in ['annual','financial','result','statement','half year','six months','quarter','audited','unaudited']):continue
    if any(k in low for k in ['agm','proxy','governance','policy','circular','director','profit warning','shareholder','company profile','safety','environmental','quality','articles of association']):continue
    title=' '.join((a.find_previous(['h3','h2','h4']).get_text(' ',strip=True) if a.find_previous(['h3','h2','h4']) else text).split())
    date=''
    m=re.search(r'\b\d{1,2}\s+[A-Za-z]{3}\s+20\d{2}\b',text)
    if m:date=m.group(0)
    item=(title,href,date)
    if href not in {x['url'] for x in out}:out.append({'title':title,'url':href,'publication_date':date})
with open(str(PROJECT_ROOT / 'crown_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','publication_date']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
