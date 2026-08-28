# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'unga_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=(title+' '+url).lower()
 if any(k in low for k in ['agm','governance','policy','circular','director','appointment','insider','dividend','proxy','notice','announcement','code of conduct']):continue
 if any(k in low for k in ['half year','half-year','six months','h1']):freq='Semi-annual / half-year'
 elif any(k in low for k in ['quarter','q1','q2','q3','q4']):freq='Quarterly'
 elif any(k in low for k in ['annual','integrated report','financial results for the year','full year','fy ']):freq='Annual / full-year'
 else:freq='Periodic results material'
 subtype='Annual report' if any(k in low for k in ['annual','integrated report']) else 'Financial results / statements'
 years=re.findall(r'20\d{2}',title+' '+url);year=years[0] if years else ''
 if not year or (('annual' not in low and 'integrated report' not in low and 'financial results' not in low and 'half' not in low and 'six months' not in low) ):continue
 key=('Unga Group PLC',url)
 if key in existing:continue
 rows.append({'record_id':'','issuer':'Unga Group PLC','ticker':'UNGA','report_frequency':freq,'document_subtype':subtype,'report_year_label':year,'webpage_title':title,'source_page_url':x['source_page_url'],'download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});existing.add(key);new+=1
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
