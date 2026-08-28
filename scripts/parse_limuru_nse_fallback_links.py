# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.nse.co.ke_listed-company-announcements__1787828536471.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for card in soup.select('.nse_col_3'):
 h=card.find(['h2','h3','h4'])
 a=card.find('a',href=True)
 if not h or not a:continue
 title=' '.join(h.get_text(' ',strip=True).split()); url=urljoin('https://www.nse.co.ke/listed-company-announcements/',a['href']); low=(title+' '+url).lower()
 if 'limuru' not in low:continue
 if not any(k in low for k in ['audited','financial','results','statement','annual','interim','quarter','half']):continue
 out.append({'title':title,'url':url,'filename':url.rsplit('/',1)[-1],'source_page':'https://www.nse.co.ke/listed-company-announcements/','source_tier':'NSE/exchange fallback'})
with open(str(PROJECT_ROOT / 'limuru_nse_fallback_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename','source_page','source_tier']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
