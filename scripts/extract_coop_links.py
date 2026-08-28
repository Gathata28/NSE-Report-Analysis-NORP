# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.co-opbank.co.ke_investor-relations_integrated-reports__1787815802541.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
    text=re.sub(r'\s+',' ',a.get_text(' ',strip=True))
    href=urljoin('https://www.co-opbank.co.ke/investor-relations/integrated-reports/',a['href'])
    if text and ('.pdf' in href.lower() or 'integrated report' in text.lower() or 'financial' in text.lower()):
        rows.append({'link_text':text,'direct_url':href})
with open(str(PROJECT_ROOT / 'coop_integrated_links.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['link_text','direct_url']);w.writeheader();w.writerows(rows)
print('rows',len(rows))
for r in rows: print(r['link_text'],'|',r['direct_url'])
