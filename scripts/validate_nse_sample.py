# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,time,urllib.parse,requests
from pathlib import Path
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
rows=list(csv.DictReader(open(str(PROJECT_ROOT / 'nse_reports_normalized.csv'),encoding='utf-8')))
groups=defaultdict(list)
for r in rows:groups[r['issuer']].append(r)
sample=[]
for issuer,rs in groups.items():
 rs=sorted(rs,key=lambda r:(r.get('report_year_label',''),r['record_id']))
 picks=[]
 # Earliest, latest, and frequency-diverse representatives.
 for r in rs:
  if r.get('report_frequency') not in {x.get('report_frequency') for x in picks}:picks.append(r)
 for r in (rs[0],rs[-1]):
  if r not in picks:picks.append(r)
 sample.extend(picks[:5])
headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36','Accept':'application/pdf,*/*;q=0.8'}
def one(r):
 u=r['download_url']
 try:
  h=requests.get(u,headers={**headers,'Range':'bytes=0-1023'},timeout=(6,12),allow_redirects=True,stream=True)
  result={'record_id':r['record_id'],'download_url':u,'validation_status':str(h.status_code),'content_type_observed':h.headers.get('content-type',''),'final_url':h.url,'validation_method':'GET range','error':''};h.close();return result
 except Exception as e:return {'record_id':r['record_id'],'download_url':u,'validation_status':'ERROR','content_type_observed':'','final_url':'','validation_method':'GET range','error':str(e)[:300]}
res=[]
with ThreadPoolExecutor(max_workers=12) as ex:
 fs=[ex.submit(one,r) for r in sample]
 for f in as_completed(fs):res.append(f.result())
res.sort(key=lambda r:r['record_id'])
out=Path(str(PROJECT_ROOT / 'nse_link_validation_sample.csv'))
with out.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record_id','download_url','validation_status','content_type_observed','final_url','validation_method','error']);w.writeheader();w.writerows(res)
print('sample_records',len(sample),'validated',len(res),'statuses',Counter(r['validation_status'] for r in res).most_common())
