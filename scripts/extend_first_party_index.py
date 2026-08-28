# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re,requests
from pathlib import Path
from bs4 import BeautifulSoup

INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')))
seen={(r['issuer'],r['download_url']) for r in rows}
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})

def classify(title):
    low=title.lower()
    year=''
    m=re.search(r'(20\d{2})',title)
    if m: year=m.group(1)
    elif re.search(r'(FY|HY|H1)\s?\d{2}',title,re.I): year=re.search(r'(FY|HY|H1)\s?\d{2}',title,re.I).group(0)
    if 'integrated report' in low or 'annual report' in low or ('fy' in low and 'financial' in low): freq='Annual / full-year'
    elif re.search(r'(h1|hy|half|interim)',low): freq='Semi-annual / half-year'
    elif re.search(r'\bq[1-4]\b',low): freq='Quarterly'
    else: freq='Periodic results material'
    if 'integrated report' in low or 'annual report' in low: subtype='Annual report'
    elif 'financial statement' in low or 'financials' in low: subtype='Financial statements'
    else: subtype='Periodic results material'
    return year,freq,subtype

def add(issuer,ticker,page_title,page_url,title,url):
    key=(issuer,url)
    if key in seen:return
    status='error';ctype=''
    try:
        r=s.get(url,stream=True,timeout=45,allow_redirects=True);status=str(r.status_code);ctype=r.headers.get('content-type','');r.close()
    except Exception as e:status='error:'+type(e).__name__
    year,freq,subtype=classify(title)
    rows.append({'issuer':issuer,'ticker':ticker,'report_frequency':freq,'document_subtype':subtype,'report_year_label':year,'webpage_title':page_title,'source_page_url':page_url,'download_url':url,'http_status':status,'content_type':ctype,'source_tier':'Issuer website','record_id':''})
    seen.add(key)

# Co-op integrated archive: exact title is the h3 immediately above each PDF download.
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.co-opbank.co.ke_investor-relations_integrated-reports__1787815802541.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
for a in soup.find_all('a',href=True):
    url=a['href']
    if not url.lower().endswith('.pdf'):continue
    box=a
    title=''
    for _ in range(6):
        box=box.parent
        if box is None:break
        h=box.find(['h2','h3','h4'])
        if h:title=re.sub(r'\s+',' ',h.get_text(' ',strip=True));break
    if title and 'integrated report' in title.lower():
        add('Co-operative Bank of Kenya PLC','COOP','Integrated Reports | Co-operative Bank of Kenya','https://www.co-opbank.co.ke/investor-relations/integrated-reports/',title,url)
# Co-op financial-statements archive.
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.co-opbank.co.ke_investor-relations_financial-statements__1787815857152.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
for a in soup.find_all('a',href=True):
    url=a['href']
    if not url.lower().endswith('.pdf'):continue
    box=a;title=''
    for _ in range(6):
        box=box.parent
        if box is None:break
        h=box.find(['h2','h3','h4'])
        if h:title=re.sub(r'\s+',' ',h.get_text(' ',strip=True));break
    if title and 'financial' in title.lower():
        add('Co-operative Bank of Kenya PLC','COOP','Financial Statements | Co-operative Bank of Kenya','https://www.co-opbank.co.ke/investor-relations/financial-statements/',title,url)
# KCB integrated reports from the issuer archive extraction.
for r in csv.DictReader(open(str(PROJECT_ROOT / 'issuer_archive_links_sample.csv'),encoding='utf-8')):
    if r['issuer_context']=='KCB Group' and 'Integrated Report' in r['link_text'] and '/download/' in r['direct_url']:
        add('KCB Group PLC','KCB','Integrated Reports | KCB Bank','https://kcbgroup.com/integrated-reports',r['link_text'],r['direct_url'])
# assign stable IDs after extension
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']);w.writeheader();w.writerows(rows)
print('total',len(rows),'new',len(rows)-122)
from collections import Counter
print('issuers',Counter(r['issuer'] for r in rows))
print('status',Counter(r['http_status'] for r in rows))
