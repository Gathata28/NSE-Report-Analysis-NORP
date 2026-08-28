# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'nbk_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=(title+' '+x['filename']).lower();ys=re.findall(r'20\d{2}',title+' '+x['filename']);year=ys[0] if ys else ''
 if not year:continue
 if any(k in low for k in ['q1','q3','march','june','september','sep']):freq='Quarterly' if any(k in low for k in ['q1','q3','march','september','sep']) else 'Semi-annual / half-year'
 elif any(k in low for k in ['h1','half','june']):freq='Semi-annual / half-year'
 else:freq='Annual / full-year'
 subtype='Results booklet / abridged report' if any(k in low for k in ['abridged','summary']) else 'Financial results / statements'
 key=('National Bank of Kenya PLC',url)
 if key in existing:continue
 readable=title.replace('_',' ').replace('-',' ').replace('.pdf','').strip()
 rows.append({'record_id':'','issuer':'National Bank of Kenya PLC','ticker':'NBK','report_frequency':freq,'document_subtype':subtype,'report_year_label':year,'webpage_title':readable,'source_page_url':'https://www.nationalbank.co.ke/investor-relations','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Historical issuer website'});existing.add(key);new+=1
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
