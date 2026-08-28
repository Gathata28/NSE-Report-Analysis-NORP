# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));seen={(r['issuer'],r['download_url']) for r in rows};new=0
source_rows=list(csv.DictReader(open(str(PROJECT_ROOT / 'nmg_report_links.csv'),encoding='utf-8')))
for x in source_rows:
    url=x['url'];title=x['title']
    key=('Nation Media Group PLC',url)
    if key in seen:continue
    m=re.search(r'(20\d{2})',title+' '+url);year=m.group(1) if m else ''
    rows.append({'record_id':'','issuer':'Nation Media Group PLC','ticker':'NMG','report_frequency':'Annual / full-year','document_subtype':'Annual report and financial statements','report_year_label':year,'webpage_title':'Financial Reports - The Nation Media Group','source_page_url':'https://www.nationmedia.com/investor-relations/financial-reports/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});seen.add(key);new+=1
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier','publication_date']);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
