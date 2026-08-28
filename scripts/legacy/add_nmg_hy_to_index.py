# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')))
url='https://www.nationmedia.com/wp-content/uploads/2026/08/H1-2026-Results.pdf'
if not any(r['download_url']==url for r in rows):
    rows.append({'record_id':'','issuer':'Nation Media Group PLC','ticker':'NMG','report_frequency':'Semi-annual / half-year','document_subtype':'Unaudited financial results','report_year_label':'2026','webpage_title':'NMG HY2026 Results - The Nation Media Group','source_page_url':'https://www.nationmedia.com/investor_news/nmg-hy2026-results/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf','source_tier':'Issuer website','publication_date':'2026-08-20'})
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier','publication_date']);w.writeheader();w.writerows(rows)
print('total',len(rows))
