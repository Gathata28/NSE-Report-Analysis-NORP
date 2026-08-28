# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from pathlib import Path
p=Path(str(PROJECT_ROOT / 'historical_nse_universe.csv'))
rows=list(csv.DictReader(p.open(encoding='utf-8')))
if not any(r.get('ticker')=='NBK' for r in rows):
 rows.append({'legal_or_display_name':'National Bank of Kenya PLC','ticker':'NBK','sector':'BANKING','isin':'','status_as_of_2026-08-27':'Historical issuer; absorbed by KCB Group','status_source_url':'https://www.nationalbank.co.ke/investor-relations','former_official_site':'https://www.nationalbank.co.ke/investor-relations','last_known_listing_or_disclosure_period':'2026 financial disclosures remain on official former-issuer archive','archive_coverage_status':'64 official annual/periodic report links indexed in master report index','notes':'Official National Bank investor-relations page states KCB Group acquired 100% of National Bank and preserves National Bank-branded disclosures. This row is a historical identity, not a current-NSE issuer.'})
fields=list(rows[0].keys())
with p.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('historical_rows',len(rows),'nbk_present',any(r.get('ticker')=='NBK' for r in rows))
