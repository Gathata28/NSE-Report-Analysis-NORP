# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
path=Path(str(PROJECT_ROOT / 'ncba_quarterly.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
rows=[]
for card in soup.select('a.report-card'):
    a=card
    if not a or not a.get('href'):continue
    h=card.find(['h2','h3','h4'])
    title=re.sub(r'\s+',' ',h.get_text(' ',strip=True) if h else '')
    date=''
    for x in card.find_all(['h2','h3','h4']):
        t=re.sub(r'\s+',' ',x.get_text(' ',strip=True))
        if re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+20\d{2}',t):date=t
    if title:
        rows.append({'title':title,'publication_date':date,'source_page_url':'https://ncbagroup.com/quarterly-earnings/','direct_url':urljoin('https://ncbagroup.com/quarterly-earnings/',a['href']),'css_class':card.get('class','')})
with open(str(PROJECT_ROOT / 'ncba_quarterly_links.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print('rows',len(rows))
for r in rows:print(r['title'],'|',r['publication_date'],'|',r['direct_url'])
