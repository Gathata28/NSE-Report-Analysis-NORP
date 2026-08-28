# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));seen={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'cic_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=(title+' '+url).lower()
 if any(k in low for k in ['asset management','asset ut','unit trust','cicam','board charter','agm','governance','proxy','circular','poll','question','appointment','bonus','policy','shareholder notice']):continue
 if 'cic' not in low:continue
 issuer='CIC Insurance Group PLC';key=(issuer,url)
 if key in seen:continue
 if any(k in low for k in ['half year','h1','second quarter','q2']):freq='Semi-annual / half-year'
 elif any(k in low for k in ['q1','q3','q4','quarter']):freq='Quarterly'
 elif any(k in low for k in ['annual','full year','financial report','financial results','integrated financial']):freq='Annual / full-year'
 else:freq='Periodic results material'
 sub='Annual report' if 'annual' in low or 'integrated financial report' in low else 'Financial results / statements'
 m=re.search(r'(20\d{2})',title+' '+url);year=m.group(1) if m else ''
 if not year:continue
 rows.append({'record_id':'','issuer':issuer,'ticker':'CIC','report_frequency':freq,'document_subtype':sub,'report_year_label':year,'webpage_title':'Investor Relations | CIC Group','source_page_url':'https://www.cicinsurancegroup.com/investor-relations/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});seen.add(key);new+=1
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
