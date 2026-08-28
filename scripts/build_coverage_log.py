# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from pathlib import Path
from collections import defaultdict
universe=list(csv.DictReader(open(str(PROJECT_ROOT / 'current_nse_universe.csv'),encoding='utf-8')))
sites={r['ticker']:r['official_site_url'] for r in csv.DictReader(open(str(PROJECT_ROOT / 'current_nse_universe_with_sites.csv'),encoding='utf-8'))}
idx=list(csv.DictReader(open(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'),encoding='utf-8')))
by=defaultdict(list)
for r in idx:by[r['ticker']].append(r)
rows=[]
for u in universe:
    t=u['ticker']; records=by.get(t,[])
    rows.append({'sector':u['sector'],'issuer_name':u['issuer_name'],'ticker':t,'isin':u['isin'],'official_site_url':sites.get(t,''),'indexed_report_records':len(records),'annual_records':sum(r['report_frequency']=='Annual / full-year' for r in records),'semiannual_records':sum(r['report_frequency']=='Semi-annual / half-year' for r in records),'quarterly_records':sum(r['report_frequency']=='Quarterly' for r in records),'coverage_status':'indexed first-party records' if records else 'not yet indexed; archive search required'})
with open(str(PROJECT_ROOT / 'current_issuer_coverage_log.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print('universe',len(rows),'with_records',sum(x['indexed_report_records']>0 for x in rows),'without_records',sum(x['indexed_report_records']==0 for x in rows))
for x in rows:
 if x['indexed_report_records']==0:print(x['ticker'],x['issuer_name'],x['official_site_url'])
