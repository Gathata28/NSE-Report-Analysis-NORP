# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
html=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.nse.co.ke_listed-companies__1787818215539.html')).read_text(errors='ignore')
soup=BeautifulSoup(html,'html.parser')
# Text-based extraction around issuer cards; preserve the official names/tickers/ISINs as displayed.
text='\n'.join(x.strip() for x in soup.get_text('\n').splitlines() if x.strip())
sectors=['AGRICULTURAL','AUTOMOBILES AND ACCESSORIES','BANKING','COMMERCIAL AND SERVICES','CONSTRUCTION AND ALLIED','ENERGY AND PETROLEUM','INSURANCE','INVESTMENT','INVESTMENT SERVICES','MANUFACTURING AND ALLIED','TELECOMMUNICATION AND TECHNOLOGY','REAL ESTATE INVESTMENT TRUST','EXCHANGE TRADED FUND']
lines=text.splitlines(); rows=[]; sector=''
for i,line in enumerate(lines):
    u=line.upper()
    if u in sectors: sector=line; continue
    if line.startswith('Trading Symbol:') or line.startswith('Trading Symbol: '):
        ticker=line.split(':',1)[1].strip()
        # nearest preceding line is usually issuer name, but avoid labels
        name=''
        for j in range(i-1,max(-1,i-8),-1):
            cand=lines[j].strip()
            if cand and not cand.startswith(('ISIN','Trading Symbol','SCOM','KCB','EQTY','BRIT','CTUM')) and cand.upper() not in sectors:
                name=cand;break
        isin=''
        for j in range(i+1,min(len(lines),i+5)):
            if lines[j].startswith('ISIN CODE:') or lines[j].startswith('ISIN:'):
                isin=lines[j].split(':',1)[1].strip();break
        if name and ticker and not any(r['ticker']==ticker and r['isin']==isin for r in rows):rows.append({'sector':sector,'issuer_name':name,'ticker':ticker,'isin':isin,'status':'current NSE page'})
with open(str(PROJECT_ROOT / 'current_nse_universe.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['sector','issuer_name','ticker','isin','status']);w.writeheader();w.writerows(rows)
print('rows',len(rows));[print(r) for r in rows]
