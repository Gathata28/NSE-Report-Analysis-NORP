# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,json
src=str(PROJECT_ROOT / 'newgold_downloads_api.json')
rows=json.load(open(src,encoding='utf-8'))
out=[]
for r in rows:
 title=' '.join(str(r.get('title') or '').split()); typ=' '.join(str(r.get('type') or '').split()); fid=str(r.get('downloadFileId') or '').strip()
 low=(title+' '+typ).lower()
 if not fid or 'annual financial statement' not in low or 'no material changes' in low or 'foreign financial statements' in low:continue
 out.append({'title':title,'year':title[:4] if title[:4].isdigit() else '','url':'https://aiss.absa.africa/api/client/downloads/file/'+fid,'filename':fid+'.pdf','source_page':'https://aiss.absa.africa/product/etf/ZAE000060067/GHA/downloads','published_date':str(r.get('date') or '')})
with open(str(PROJECT_ROOT / 'newgold_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','year','url','filename','source_page','published_date']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
