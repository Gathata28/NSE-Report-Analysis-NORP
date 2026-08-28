# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re,requests
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')))
seen={(r['issuer'],r['download_url']) for r in rows}
s=requests.Session();s.headers.update({'User-Agent':'Mozilla/5.0'})
for x in csv.DictReader(open(str(PROJECT_ROOT / 'eabl_financial_results_links.csv'),encoding='utf-8')):
    title=x['title'];url=x['url']
    if not re.search(r'(Full Year|Half Year)',title,re.I):continue
    if ( 'EABL PLC',url) in seen:continue
    low=title.lower()
    if 'full year' in low: freq='Annual / full-year'
    elif 'half year' in low: freq='Semi-annual / half-year'
    else: freq='Periodic results material'
    if 'financials' in low or 'financial results' in low:subtype='Financial results / statements'
    elif 'presentation' in low:subtype='Investor presentation'
    elif 'press release' in low or 'press ad' in low:subtype='Results announcement'
    else:subtype='Periodic results material'
    m=re.search(r'(20\d{2})',title);year=m.group(1) if m else ''
    try:
        r=s.get(url,stream=True,timeout=30,allow_redirects=True);status=str(r.status_code);ctype=r.headers.get('content-type','');r.close()
    except Exception as e:status='error:'+type(e).__name__;ctype=''
    rows.append({'record_id':'','issuer':'East African Breweries PLC','ticker':'EABL','report_frequency':freq,'document_subtype':subtype,'report_year_label':year,'webpage_title':'Financial Results | EABL','source_page_url':'https://www.eabl.com/investors/financial-results','download_url':url,'http_status':status,'content_type':ctype,'source_tier':'Issuer website'})
    seen.add(('EABL PLC',url))
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',len(rows)-148)
from collections import Counter
print(Counter(r['issuer'] for r in rows));print(Counter(r['http_status'] for r in rows))
