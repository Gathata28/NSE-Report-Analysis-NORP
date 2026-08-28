# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,json
from urllib.parse import urljoin
src=str(PROJECT_ROOT / 'bk_financial_reports_api.json')
data=json.load(open(src,encoding='utf-8'))
out=[]
for group in data.get('data',[]):
 a=group.get('attributes') or {}; rt=str(a.get('reportType') or '')
 for r in a.get('report') or []:
  title=' '.join(str(r.get('title') or '').split()); year=str(r.get('year') or '')
  d=((r.get('reportDocument') or {}).get('data') or {}).get('attributes') or {}
  u=str(d.get('url') or '').strip()
  low=(rt+' '+title+' '+u).lower()
  if not u or any(k in low for k in ['agm','policy','manual','form','tariff','governance','sustainability','risk charter','investor presentation','rights issue','dividend','important dates','shareholder']):continue
  if not any(k in low for k in ['annual','financial','result','quarter','half year','half-year','interim','six month','statement']):continue
  url=urljoin('https://bk.rw',u)
  out.append({'title':title,'year':year,'report_type':rt,'url':url,'filename':u.rsplit('/',1)[-1],'source_page':'https://bk.rw/en/about/document-center'})
seen=set();rows=[]
for r in out:
 key=(r['title'],r['year'],r['url'])
 if key not in seen:rows.append(r);seen.add(key)
with open(str(PROJECT_ROOT / 'bk_group_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','year','report_type','url','filename','source_page']);w.writeheader();w.writerows(rows)
print('records',len(rows))
for r in rows[:80]:print(r)
