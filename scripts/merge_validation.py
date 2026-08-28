# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from pathlib import Path
master=Path(str(PROJECT_ROOT / 'nse_reports_normalized.csv'))
val={r['record_id']:r for r in csv.DictReader(open(str(PROJECT_ROOT / 'nse_link_validation_sample.csv'),encoding='utf-8'))}
out=Path(str(PROJECT_ROOT / 'nse_reports_normalized_validated.csv'))
rows=[]
for r in csv.DictReader(master.open(encoding='utf-8')):
    row=dict(r);v=val.get(r['record_id'])
    if v:
        row['validation_date']='2026-08-27'
        row['validation_method']=v['validation_method']
        row['link_verification_status']=f"HTTP {v['validation_status']} sample-validated"
        row['content_type_observed']=v['content_type_observed']
        row['final_url']=v['final_url']
        row['validation_error']=v['error']
        if v['validation_status'] in ('200','206') and 'pdf' in v['content_type_observed'].lower():row['link_verification_status']+='; PDF content-type observed'
        elif v['validation_status'] in ('200','206'):row['link_verification_status']+='; non-PDF content-type observed'
        elif v['validation_status']=='403':row['link_verification_status']+='; issuer/CDN access denied in the current environment'
        elif v['validation_status']=='ERROR':row['link_verification_status']+='; request error'
    else:
        row['link_verification_status']=row.get('link_verification_status') or 'Official source-page linkage captured; HTTP sample validation pending'
        row['content_type_observed']='';row['final_url']='';row['validation_error']=''
    rows.append(row)
fields=list(rows[0].keys())
with out.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
from collections import Counter
print('rows',len(rows),'validated_sample',len(val),'status',Counter(r['link_verification_status'].split(';')[0] for r in rows).most_common())
