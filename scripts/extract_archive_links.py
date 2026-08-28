# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
import re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

inputs = [
    ('KCB Group', 'https://kcbgroup.com/integrated-reports', Path(str(PROJECT_ROOT / 'data' / 'sources' / 'kcbgroup.com_integrated-reports_1787814844913.html'))),
    ('Equity Group', 'https://equitygroupholdings.com/investor-relations/', Path(str(PROJECT_ROOT / 'data' / 'sources' / 'equitygroupholdings.com_investor-relations__1787815113942.html'))),
    ('AfricanFinancials example', 'https://africanfinancials.com/document/ke-nse-2025-ar-00/', Path(str(PROJECT_ROOT / 'data' / 'sources' / 'africanfinancials.com_document_ke-nse-2025-ar-00__1787814922153.html'))),
]
rows = []
for issuer, page_url, path in inputs:
    soup = BeautifulSoup(path.read_text(errors='ignore'), 'html.parser')
    for a in soup.find_all('a', href=True):
        href = urljoin(page_url, a['href'])
        text = re.sub(r'\s+', ' ', a.get_text(' ', strip=True))
        if text and ('.pdf' in href.lower() or 'download' in href.lower() or 'report' in text.lower() or 'financial' in text.lower() or 'statement' in text.lower() or 'booklet' in text.lower()):
            rows.append({'issuer_context': issuer, 'archive_page_url': page_url, 'link_text': text, 'direct_url': href})
with open(str(PROJECT_ROOT / 'issuer_archive_links_sample.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
print('rows', len(rows))
for r in rows[:80]: print(r)
