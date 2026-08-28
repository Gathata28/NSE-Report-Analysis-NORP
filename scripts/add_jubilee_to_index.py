# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));seen={(r['issuer'],r['download_url']) for r in rows};new=0
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'data' / 'sources' / 'jubileeinsurance.com_group_investor-relations_annual-reports__1787819047878.html')).read_text(errors='ignore'),'html.parser')
for a in soup.find_all('a',href=True):
 url=a['href'];low=url.lower()
 if '.pdf' not in low or not any(k in low for k in ['annual','report']):continue
 if any(k in low for k in ['whistle','policy','governance']):continue
 m=re.search(r'(20\d{2})',url)
 if not m:continue
 key=('Jubilee Holdings PLC',url)
 if key in seen:continue
 rows.append({'record_id':'','issuer':'Jubilee Holdings PLC','ticker':'JUB','report_frequency':'Annual / full-year','document_subtype':'Annual integrated report','report_year_label':m.group(1),'webpage_title':'Find Jubilee Insurance Annual and Integrated Reports','source_page_url':'https://jubileeinsurance.com/group/investor-relations/annual-reports/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});seen.add(key);new+=1
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
