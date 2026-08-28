# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));seen={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'britam_annual_links.csv'),encoding='utf-8')):
 issuer='Britam Holdings PLC';url=x['url'];key=(issuer,url)
 if key in seen or not x['year']:continue
 rows.append({'record_id':'','issuer':issuer,'ticker':'BRIT','report_frequency':'Annual / full-year','document_subtype':'Annual report and financial statements','report_year_label':x['year'],'webpage_title':'Unveiling Britam’s Impressive Annual Reports | Download Now','source_page_url':'https://www.britam.com/investor-relations/annual-reports','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});seen.add(key);new+=1
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
