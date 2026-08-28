# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,time,threading,requests,urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from collections import defaultdict
master=Path(str(PROJECT_ROOT / 'nse_reports_normalized.csv'))
out=Path(str(PROJECT_ROOT / 'nse_link_validation.csv'))
rows=list(csv.DictReader(master.open(encoding='utf-8')))
locks=defaultdict(threading.Lock);last=defaultdict(float)
headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36','Accept':'application/pdf,*/*;q=0.8'}
def one(r):
 u=r.get('download_url','');domain=urllib.parse.urlsplit(u).netloc
 with locks[domain]:
  wait=.08-(time.time()-last[domain])
  if wait>0:time.sleep(wait)
  last[domain]=time.time()
 try:
  h=requests.head(u,headers=headers,timeout=(8,20),allow_redirects=True)
  status=h.status_code;ctype=h.headers.get('content-type','');final=h.url;method='HEAD'
  if status>=400 or not ctype:
   g=requests.get(u,headers={**headers,'Range':'bytes=0-1023'},timeout=(8,25),allow_redirects=True,stream=True)
   status=g.status_code;ctype=g.headers.get('content-type','');final=g.url;method='GET range'
   g.close()
  return {'record_id':r['record_id'],'download_url':u,'validation_status':str(status),'content_type_observed':ctype,'final_url':final,'validation_method':method,'error':''}
 except Exception as e:
  return {'record_id':r['record_id'],'download_url':u,'validation_status':'ERROR','content_type_observed':'','final_url':'','validation_method':'','error':str(e)[:300]}
results=[]
with ThreadPoolExecutor(max_workers=12) as ex:
 futs=[ex.submit(one,r) for r in rows]
 for i,f in enumerate(as_completed(futs),1):
  results.append(f.result())
  if i%100==0:print('validated',i)
results.sort(key=lambda x:int(x['record_id'].split('-')[-1]) if x['record_id'].startswith('NSE-') else 0)
with out.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['record_id','download_url','validation_status','content_type_observed','final_url','validation_method','error']);w.writeheader();w.writerows(results)
from collections import Counter
print('total',len(results),'statuses',Counter(x['validation_status'] for x in results).most_common())
