# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'centum_financial_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=title.lower();fn=x['filename'].lower();combined=low+' '+fn
 if 'half year' in low or 'half-year' in low or low.startswith('hy') or 'interim' in low or 'half_year' in low:freq='Semi-annual / half-year'
 elif 'full year' in low or 'full-year' in low or low.startswith('fy') or 'year results' in low or 'audited results' in low:freq='Annual / full-year'
 elif 'quarter' in combined or re.search(r'\bq[1-4]\b',combined):freq='Quarterly'
 elif any(k in combined for k in ['half','hy']):freq='Semi-annual / half-year'
 else:freq='Periodic results material'
 if any(k in combined for k in ['presentation','briefing','commentary','infograph']):sub='Results presentation / announcement'
 elif any(k in combined for k in ['financial statement','financials','results']):sub='Financial results / statements'
 else:sub='Periodic results material'
 if 'fy25' in combined:year='2025'
 elif 'fy24' in combined:year='2024'
 elif 'fy23' in combined:year='2023'
 elif 'fy22' in combined:year='2022'
 elif 'fy21' in combined:year='2021'
 elif 'fy20' in combined:year='2020'
 elif 'fy19' in combined:year='2019'
 elif 'fy18' in combined:year='2018'
 elif 'fy17' in combined:year='2017'
 elif 'fy16' in combined:year='2016'
 elif 'fy14' in combined:year='2014'
 elif 'hy19' in combined:year='2019'
 elif 'hy20' in combined:year='2020'
 elif 'hy21' in combined:year='2021'
 elif 'hy22' in combined:year='2022'
 elif 'hy23' in combined:year='2023'
 elif 'hy24' in combined:year='2024'
 elif 'hy25' in combined:year='2025'
 elif 'hy2016' in combined or 'hy_2016' in combined:year='2016'
 elif 'hy-2015' in combined:year='2015'
 else:
  ys=re.findall(r'20\d{2}',title+' '+url);year=ys[0] if ys else ''
 if not year:continue
 key=('Centum Investment Company PLC',url)
 if key in existing:continue
 rows.append({'record_id':'','issuer':'Centum Investment Company PLC','ticker':'CTUM','report_frequency':freq,'document_subtype':sub,'report_year_label':year,'webpage_title':title,'source_page_url':'https://centum.co.ke/centum-financial-results/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});existing.add(key);new+=1
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
