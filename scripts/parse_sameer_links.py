# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'sameerafrica.com_financial-reports__1787825615404.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://sameerafrica.com/financial-reports/',a['href'])
 title=' '.join(a.get_text(' ',strip=True).split())
 low=(href+' '+title).lower()
 if any(x in low for x in ['agm','polling','proxy','notice','minutes','policy','profit warning','governance','charter']):continue
 if href.rstrip('/').endswith('financial-reports') or '#' in href:continue
 if title.lower() in ('about sameer africa','annual report and financial statements','financial results'):continue
 if not any(x in low for x in ['.pdf','.xlsx','.xls','.doc','annual','financial','interim','result','report']):continue
 if not title or title.lower() in ('download','download file','view'):
  title=re.sub(r'[_-]+',' ',href.rsplit('/',1)[-1].split('?',1)[0])
 if href not in [r['url'] for r in out]:out.append({'title':title,'url':href,'filename':href.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'sameer_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out: print(r)
