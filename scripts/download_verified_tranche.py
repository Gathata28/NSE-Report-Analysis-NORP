# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv, hashlib, re
from pathlib import Path
import requests

base=Path(str(PROJECT_ROOT / 'downloads'))
base.mkdir(exist_ok=True)
rows=list(csv.DictReader(open(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'),encoding='utf-8')))
s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
manifest=[]
for row in rows:
    if row['http_status']!='200': continue
    safe=re.sub(r'[^A-Za-z0-9._-]+','_',row['record_id']+'_'+row['issuer']+'_'+row['webpage_title']+'_'+row['report_year_label']+'_'+row['document_subtype'])[:180]
    path=base/(safe+'.pdf')
    try:
        r=s.get(row['download_url'],timeout=60,stream=True)
        r.raise_for_status()
        h=hashlib.sha256(); n=0
        with path.open('wb') as f:
            for chunk in r.iter_content(1024*128):
                if chunk:
                    f.write(chunk); h.update(chunk); n+=len(chunk)
        manifest.append({'record_id':row['record_id'],'path':str(path),'bytes':n,'sha256':h.hexdigest(),'download_status':'saved'})
    except Exception as e:
        manifest.append({'record_id':row['record_id'],'path':str(path),'bytes':0,'sha256':'','download_status':'error:'+type(e).__name__})
with open(str(PROJECT_ROOT / 'verified_download_manifest.csv'),'w',newline='',encoding='utf-8') as f:
    import csv as c
    w=c.DictWriter(f,fieldnames=['record_id','path','bytes','sha256','download_status']); w.writeheader(); w.writerows(manifest)
print('saved',sum(x['download_status']=='saved' for x in manifest),'failed',sum(x['download_status']!='saved' for x in manifest))
for x in manifest: print(x)
