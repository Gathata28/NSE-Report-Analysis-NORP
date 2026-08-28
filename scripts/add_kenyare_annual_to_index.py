# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'kenyare_annual_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];fn=x['filename'];low=(title+' '+fn).lower()
 ys=re.findall(r'20\d{2}',title+' '+fn);year=ys[0] if ys else ''
 if not year:continue
 key=('Kenya Re-Insurance Corporation PLC',url)
 if key in existing:continue
 readable=fn.replace('%20',' ').replace('_',' ').replace('%28','(').replace('%29',')')
 rows.append({'record_id':'','issuer':'Kenya Re-Insurance Corporation PLC','ticker':'KNRE','report_frequency':'Annual / full-year','document_subtype':'Annual report','report_year_label':year,'webpage_title':readable,'source_page_url':'https://www.kenyare.co.ke/investor-relations/agm/annual-reports','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});existing.add(key);new+=1
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
