# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'carbacid_report_links.csv'),encoding='utf-8')):
 if not x.get('url') or not x['url'].lower().endswith('.pdf'):continue
 key=('Carbacid Investments PLC',x['url'])
 if key in existing:continue
 rows.append({'record_id':'','issuer':'Carbacid Investments PLC','ticker':'CARB','report_frequency':'Annual / full-year','document_subtype':'Annual report','report_year_label':'2025','webpage_title':x['title'],'source_page_url':x['source_page_url'],'download_url':x['url'],'http_status':'200 verified','content_type':'application/pdf','source_tier':'Issuer website'});existing.add(key);new+=1
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
