# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup
from pathlib import Path
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'kq_annual_reports.html')).read_text(errors='ignore'),'html.parser')
for i,a in enumerate(soup.find_all('a',href=True)):
 href=a['href']; text=' '.join(a.get_text(' ',strip=True).split())
 if '.pdf' in href.lower():
  print(i,repr(text),href)
