# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'kq_financial_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=(title+' '+url).lower();fn=x['filename'].lower()
 if any(k in low for k in ['quarter','q1','q2','q3','q4']):freq='Quarterly'
 elif any(k in low for k in ['half','h1','six-month','six_month']):freq='Semi-annual / half-year'
 elif any(k in low for k in ['fy','full-year','full year','twelve-month','twelve_month','2025','2024','2023','2022','2021','2020','2019','2018']) and not any(k in low for k in ['half','h1','six-month','six_month']):freq='Annual / full-year'
 else:freq='Periodic results material'
 if any(k in fn for k in ['presentation','briefing','press-release','chairman','commentary']):sub='Results presentation / announcement'
 elif 'auditor' in fn:sub='Financial results / statements'
 else:sub='Financial results / statements'
 if 'fy25' in low:year='2025'
 elif 'fy24' in low:year='2024'
 elif 'fy23' in low:year='2023'
 else:
  ys=re.findall(r'20\d{2}',title+' '+url);year=ys[0] if ys else ''
 if not year:continue
 key=('Kenya Airways PLC',url)
 if key in existing:continue
 rows.append({'record_id':'','issuer':'Kenya Airways PLC','ticker':'KQ','report_frequency':freq,'document_subtype':sub,'report_year_label':year,'webpage_title':title,'source_page_url':'https://corporate.kenya-airways.com/en/investors-shareholders/financial-results/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});existing.add(key);new+=1
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
