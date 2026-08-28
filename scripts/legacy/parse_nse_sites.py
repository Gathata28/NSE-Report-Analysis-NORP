# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
html=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.nse.co.ke_listed-companies__1787818215539.html')).read_text(errors='ignore')
soup=BeautifulSoup(html,'html.parser')
rows=[]
for h in soup.find_all(['h6','h5','h4']):
    name=' '.join(h.get_text(' ',strip=True).split())
    if not name or not any(x in name.lower() for x in ['ltd','plc','group','bank','company','holdings','trust','fund','reit','africa','tea','sugar','kenya','capital','airways','media','power','pipeline','serena','scangroup','safaricom','eabl']): continue
    # Search nearby ancestor for ticker, ISIN, and external issuer link.
    parent=h
    for _ in range(8):
        parent=parent.parent
        if parent is None:break
        txt=' '.join(parent.get_text(' ',strip=True).split())
        if 'Trading Symbol' in txt and ('ISIN' in txt or 'ISIN CODE' in txt):
            break
    if parent is None:continue
    text='\n'.join(x.strip() for x in parent.get_text('\n').splitlines() if x.strip())
    tm=re.search(r'Trading Symbol:\s*([A-Za-z0-9.]+)',text,re.I); im=re.search(r'ISIN(?: CODE)?:\s*([A-Z0-9]+)',text,re.I)
    ticker=tm.group(1) if tm else '';isin=im.group(1) if im else ''
    href=''
    for a in parent.find_all('a',href=True):
        u=a['href']
        if u.startswith('http') and 'nse.co.ke' not in u and not any(z in u.lower() for z in ['facebook','twitter','linkedin','youtube']):href=u;break
    if ticker and not any(r['ticker']==ticker and r['isin']==isin for r in rows):rows.append({'issuer_name':name,'ticker':ticker,'isin':isin,'official_site_url':href})
with open(str(PROJECT_ROOT / 'current_nse_universe_with_sites.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['issuer_name','ticker','isin','official_site_url']);w.writeheader();w.writerows(rows)
print('rows',len(rows));[print(r) for r in rows]
