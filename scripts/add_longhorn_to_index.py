# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'longhorn_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=title.lower()
 if 'half year' in low or 'interim' in low:freq='Semi-annual / half-year'
 elif 'full year' in low or 'annual report' in low:freq='Annual / full-year'
 else:freq='Periodic results material'
 subtype='Results booklet / abridged report' if 'abridged' in low else ('Annual report' if 'annual report' in low else 'Financial results / statements')
 m=re.search(r'fy\s*(20\d{2})',low)
 if m:year=m.group(1)
 else:
  ys=re.findall(r'20\d{2}',title+' '+url);year=ys[0] if ys else ''
 if not year:continue
 key=('Longhorn Publishers PLC',url)
 if key in existing:continue
 rows.append({'record_id':'','issuer':'Longhorn Publishers PLC','ticker':'LKL','report_frequency':freq,'document_subtype':subtype,'report_year_label':year,'webpage_title':title,'source_page_url':'https://www.longhornpublishers.com/investor-relations/reports/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});existing.add(key);new+=1
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
