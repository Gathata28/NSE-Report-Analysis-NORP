# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup
from pathlib import Path
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'unga_annual_reports.html')).read_text(errors='ignore'),'html.parser')
for a in soup.find_all('a',href=True):
    text=' '.join(a.get_text(' ',strip=True).split())
    href=a['href']
    low=(text+' '+href).lower()
    if any(k in low for k in ['annual','financial','result','statement','report','2025','2024','2023','2022','2021','2020','2019','2018','2017','2016','2015','2014','2013','2012']):
        print(text[:180], '|', href[:500])
