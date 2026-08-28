# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from collections import Counter
path = str(PROJECT_ROOT / 'issuer_archive_links_sample.csv')
rows = list(csv.DictReader(open(path, encoding='utf-8')))
print('all rows', len(rows))
print('by issuer context', Counter(r['issuer_context'] for r in rows))
for r in rows:
    if r['direct_url'].lower().endswith('.pdf'):
        print(r['issuer_context'], '|', r['link_text'], '|', r['direct_url'])
