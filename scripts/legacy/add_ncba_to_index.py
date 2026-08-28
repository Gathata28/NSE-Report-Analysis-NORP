# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')))
seen={(r['issuer'],r['download_url']) for r in rows};new=0

def append(title,url,page_url,page_title):
    global new
    issuer='NCBA Group PLC';ticker='NCBA';key=(issuer,url)
    if key in seen:return
    low=title.lower()
    if 'annual' in low or 'integrated report' in low or 'fy' in low:freq='Annual / full-year'
    elif re.search(r'(h1|hy|half)',low):freq='Semi-annual / half-year'
    elif re.search(r'\bq[1-4]\b',low):freq='Quarterly'
    else:freq='Periodic results material'
    if 'financial' in low or 'statement' in low:sub='Financial results / statements'
    elif 'deck' in low or 'presentation' in low:sub='Investor presentation'
    elif 'press release' in low:sub='Results announcement'
    else:sub='Periodic results material'
    m=re.search(r'(20\d{2})',title);year=m.group(1) if m else ''
    rows.append({'record_id':'','issuer':issuer,'ticker':ticker,'report_frequency':freq,'document_subtype':sub,'report_year_label':year,'webpage_title':page_title,'source_page_url':page_url,'download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'})
    seen.add(key);new+=1
# annual reports
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'data' / 'sources' / 'ncbagroup.com_annual-reports__1787817157187.html')).read_text(errors='ignore'),'html.parser')
for a in soup.find_all('a',href=True):
    href=urljoin('https://ncbagroup.com/annual-reports/',a['href']);text=' '.join(a.get_text(' ',strip=True).split())
    if href.lower().endswith('.pdf'):
        parent=a;title=''
        for _ in range(6):
            parent=parent.parent
            if parent is None:break
            h=parent.find(['h2','h3','h4'])
            if h:title=' '.join(h.get_text(' ',strip=True).split());break
        append(title or text,href,'https://ncbagroup.com/annual-reports/','Annual Reports - NCBA Group')
# quarterly cards
for x in csv.DictReader(open(str(PROJECT_ROOT / 'ncba_quarterly_links.csv'),encoding='utf-8')):
    append(x['title'],x['direct_url'],x['source_page_url'],'NCBA Quartely Earnings')
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
