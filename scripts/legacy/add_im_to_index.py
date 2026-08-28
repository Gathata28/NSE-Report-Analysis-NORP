# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')))
seen={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'im_report_links.csv'),encoding='utf-8')):
    title=x['title']; url=x['url']; key=('I&M Holdings PLC',url)
    if key in seen:continue
    low=title.lower()
    if 'annual report' in low or 'annual integrated' in low or 'financials' in low and not re.search(r'(q[1-3]|hy|half|interim)',low):freq='Annual / full-year'
    elif re.search(r'(hy|half|interim)',low):freq='Semi-annual / half-year'
    elif re.search(r'\bq[1-4]\b',low):freq='Quarterly'
    elif 'financial result' in low or 'financials' in low:freq='Annual / full-year'
    else:freq='Periodic results material'
    if 'annual' in low and 'report' in low:sub='Annual report'
    elif 'financial' in low or 'financials' in low:sub='Financial results / statements'
    elif 'presentation' in low:sub='Investor presentation'
    else:sub='Periodic results material'
    m=re.search(r'(20\d{2})',title);year=m.group(1) if m else ''
    rows.append({'record_id':'','issuer':'I&M Holdings PLC / I&M Group PLC','ticker':'IMH','report_frequency':freq,'document_subtype':sub,'report_year_label':year,'webpage_title':'Financial Results, Annual Reports & Investor Presentation - I&M Group','source_page_url':'https://www.imbankgroup.com/financial-results-annual-reports-and-investor-presentation/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});seen.add(key);new+=1
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
