# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup
from pathlib import Path
import html
import json

source = Path(str(PROJECT_ROOT / 'data' / 'sources' / 'africanfinancials.com_kenya-listed-company-documents__1787814224670.html'))
soup = BeautifulSoup(source.read_text(errors='ignore'), 'html.parser')

out = {
    'forms': [],
    'selects': {},
    'document_links': [],
    'pagination_data': [],
}
for form in soup.find_all('form'):
    out['forms'].append({'action': form.get('action'), 'method': form.get('method'), 'id': form.get('id'), 'class': form.get('class')})
    for sel in form.find_all('select'):
        name = sel.get('name') or sel.get('id')
        out['selects'][name] = [{'text': o.get_text(' ', strip=True), 'value': o.get('value')} for o in sel.find_all('option')]
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(' ', strip=True)
    if '/document/' in href:
        out['document_links'].append({'title': text, 'url': href})
for el in soup.select('[data-pagination]'):
    raw = html.unescape(el.get('data-pagination', ''))
    try:
        out['pagination_data'].append(json.loads(raw))
    except Exception:
        out['pagination_data'].append({'raw': raw})
Path(str(PROJECT_ROOT / 'africanfinancials_page_metadata.json')).write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2)[:20000])
