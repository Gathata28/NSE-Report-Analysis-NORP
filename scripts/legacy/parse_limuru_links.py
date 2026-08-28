# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
html=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.limuruteaplc.com_investor-information_financial-results-accounts__1787825382110.html')).read_text(errors='ignore')
soup=BeautifulSoup(html,'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.limuruteaplc.com/investor-information/financial-results-accounts/',a['href'])
 text=' '.join(a.get_text(' ',strip=True).split())
 low=(href+' '+text).lower()
 if not any(x in low for x in ['.pdf','.xlsx','.xls','.doc']): continue
 if any(x in low for x in ['agm','proxy','notice','minutes','governance','policy']): continue
 if not any(x in low for x in ['financial','result','account','report','2021','2022']): continue
 if not text or text.lower() in ('download','download file','view'):
  text=re.sub(r'[_-]+',' ',href.rsplit('/',1)[-1].split('?',1)[0])
 if href not in [x['url'] for x in out]:out.append({'title':text,'url':href,'filename':href.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'limuru_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out: print(r)
