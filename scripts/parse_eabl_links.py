# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.eabl.com_investors_financial-results_1787816569174.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for a in soup.find_all('a',href=True):
    text=re.sub(r'\s+',' ',a.get_text(' ',strip=True))
    href=urljoin('https://www.eabl.com/investors/financial-results',a['href'])
    if href.lower().endswith('.pdf') and text:
        # keep result materials, excluding unrelated site PDFs if any
        if re.search(r'(EABL|Full Year|Half Year|financial|results|annual)',text,re.I):
            rows.append({'title':text,'url':href})
with open(str(PROJECT_ROOT / 'eabl_financial_results_links.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['title','url']);w.writeheader();w.writerows(rows)
print('rows',len(rows))
for r in rows: print(r['title'],'|',r['url'])
