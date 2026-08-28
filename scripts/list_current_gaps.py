# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
idx_rows=list(csv.DictReader(open(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'),encoding='utf-8')))
covered_names={r['issuer'].strip().lower() for r in idx_rows}
covered_tickers={r['ticker'].strip().upper() for r in idx_rows if r.get('ticker')}
for r in csv.DictReader(open(str(PROJECT_ROOT / 'current_nse_universe_with_sites.csv'),encoding='utf-8')):
    name=r['issuer_name'].strip();ticker=r['ticker'].strip().upper()
    if name.lower() not in covered_names and ticker not in covered_tickers:
        print(f"{ticker}\t{name}\t{r['official_site_url']}")
