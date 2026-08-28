# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'hfcb_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=title.lower();year=x['year']
 if x['category']=='annual-reports' or 'annual report' in low:freq='Annual / full-year';subtype='Annual report'
 elif any(k in low for k in ['q1','q2','q3','q4','march','june','sept','september']):
  freq='Quarterly' if any(k in low for k in ['q1','q3','q4','march','sept','september']) else 'Semi-annual / half-year';subtype='Financial results / statements'
 elif any(k in low for k in ['h1','hy','half']):freq='Semi-annual / half-year';subtype='Financial results / statements'
 else:freq='Annual / full-year';subtype='Financial results / statements'
 key=('HF Group PLC',url)
 if key in existing:continue
 rows.append({'record_id':'','issuer':'HF Group PLC','ticker':'HFCK','report_frequency':freq,'document_subtype':subtype,'report_year_label':year,'webpage_title':title,'source_page_url':'https://hfcb.co.ke/investor-relations','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (official HFCB API download endpoint)','source_tier':'Historical/current successor issuer website'});existing.add(key);new+=1
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier','publication_date']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
