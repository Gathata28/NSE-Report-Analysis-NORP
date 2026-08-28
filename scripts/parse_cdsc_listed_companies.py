# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup
from pathlib import Path
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'cdsc_listed_companies.html')).read_text(errors='ignore'),'html.parser')
main=soup.find('main') or soup
text='\n'.join(line.strip() for line in main.get_text('\n').splitlines() if line.strip())
Path(str(PROJECT_ROOT / 'cdsc_listed_companies_text.txt')).write_text(text,encoding='utf-8')
print(text[:20000])
