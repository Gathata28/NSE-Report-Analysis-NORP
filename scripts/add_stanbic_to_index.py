# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));seen={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'stanbic_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=title.lower()
 # Keep parent-listed Stanbic Holdings records only; subsidiary reports are noted separately as associated materials.
 if 'stanbic holdings' not in low and 'stanbic holding' not in low:continue
 issuer='Stanbic Holdings PLC';key=(issuer,url)
 if key in seen:continue
 if re.search(r'(half year|h1|hy)',low):freq='Semi-annual / half-year'
 elif re.search(r'(q1|q2|q3|q4|quarter)',low):freq='Quarterly'
 elif re.search(r'(full year|annual|december|financial statements)',low):freq='Annual / full-year'
 else:freq='Periodic results material'
 sub='Annual report' if 'annual' in low and 'report' in low else ('Financial results / statements' if any(k in low for k in ['financial','results','statement']) else ('Investor presentation' if 'presentation' in low else 'Periodic results material'))
 m=re.search(r'(20\d{2})',title+' '+url);year=m.group(1) if m else ''
 rows.append({'record_id':'','issuer':issuer,'ticker':'SBIC','report_frequency':freq,'document_subtype':sub,'report_year_label':year,'webpage_title':'Stanbic bank kenya investor relations | Stanbic Bank Kenya','source_page_url':'https://www.stanbicbank.co.ke/kenya/personal/about-us/investor-relations','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});seen.add(key);new+=1
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
