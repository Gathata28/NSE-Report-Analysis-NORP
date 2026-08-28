# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE = 'https://africanfinancials.com/kenya-listed-company-documents/'
OUT = Path(str(PROJECT_ROOT / 'africanfinancials_index.csv'))
PAGES = 310

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (research index; public pages only)'})
rows = []
seen = set()

def clean(text):
    return re.sub(r'\s+', ' ', text or '').strip()

for page in range(1, PAGES + 1):
    url = BASE if page == 1 else f'{BASE}?wpv_view_count=21075&wpv_paged={page}'
    r = session.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    # Each result is the document page link inside the view layout.
    for a in soup.select('a[href*="/document/"]'):
        href = urljoin(BASE, a.get('href', ''))
        title = clean(a.get_text(' ', strip=True))
        if not title or href.rstrip('/') in seen:
            continue
        # Derive the enclosing result block from the nearest article/item container.
        container = a
        for _ in range(8):
            container = container.parent
            if container is None:
                break
            txt = clean(container.get_text(' ', strip=True))
            if any(x in txt for x in ['Document type:', 'Published:', 'Year:', 'Period:']):
                break
        txt = clean(container.get_text(' ', strip=True) if container else '')
        doc_type = re.search(r'Document type:\s*([^P]+?)\s+Published:', txt)
        published = re.search(r'Published:\s*([A-Za-z0-9 ,]+?)(?:\s+Year:|$)', txt)
        year = re.search(r'Year:\s*(\d{4})', txt)
        period = re.search(r'Period:\s*([A-Za-z0-9]+)', txt)
        sector_country = txt.split('Year:')[-1].strip() if 'Year:' in txt else ''
        seen.add(href.rstrip('/'))
        rows.append({
            'page': page,
            'title': title,
            'source_page_url': href,
            'document_type': clean(doc_type.group(1) if doc_type else ''),
            'published': clean(published.group(1) if published else ''),
            'year': year.group(1) if year else '',
            'period': period.group(1) if period else '',
            'result_text': txt,
        })
    if page % 25 == 0:
        print(f'page {page}/{PAGES}; unique documents {len(rows)}', flush=True)
    time.sleep(0.08)

with OUT.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['page'])
    writer.writeheader()
    writer.writerows(rows)
print(f'Wrote {len(rows)} unique document pages to {OUT}')
