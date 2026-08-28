# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0

def add(title,url,source,freq,subtype,pub=''):
 global new
 key=('Family Bank Limited',url)
 if key in existing:return
 ys=re.findall(r'20\d{2}',title+' '+url);year=ys[0] if ys else ''
 if not year:return
 readable=re.sub(r'\s*\([^)]*\)\s*$','',title).strip()
 rows.append({'record_id':'','issuer':'Family Bank Limited','ticker':'FMLY','report_frequency':freq,'document_subtype':subtype,'report_year_label':year,'webpage_title':readable,'source_page_url':source,'download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website','publication_date':pub});existing.add(key);new+=1
for x in csv.DictReader(open(str(PROJECT_ROOT / 'family_annual_report_links.csv'),encoding='utf-8')):
 add(x['title'],x['url'],'https://familybank.co.ke/?page_id=1773','Annual / full-year','Annual report')
for x in csv.DictReader(open(str(PROJECT_ROOT / 'family_financial_report_links.csv'),encoding='utf-8')):
 low=x['title'].lower()
 if '31st march' in low or '31st march' in x['url'].lower() or 'q1' in low:freq='Quarterly'
 elif any(k in low for k in ['30th september','30th sept','q3']):freq='Quarterly'
 elif any(k in low for k in ['30th june','half year','h1']):freq='Semi-annual / half-year'
 else:freq='Annual / full-year'
 add(x['title'],x['url'],'https://familybank.co.ke/?page_id=654',freq,'Financial results / statements',x.get('publication_date',''))
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier','publication_date']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
