# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'bk.rw_about_document-center_1787827455755.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://bk.rw/about/document-center',a['href'])
 title=' '.join((a.get_text(' ',strip=True) or a.get('title','') or a.get('aria-label','')).split())
 parent=a.parent
 context=' '.join(parent.get_text(' ',strip=True).split()) if parent else ''
 low=(title+' '+context+' '+href).lower()
 if any(k in low for k in ['agm','proxy','resolution','circular','dividend','tariff','manual','form','policy','notice','appointment','investor day','credit facility','mortgage','service charter','customer contract','customer form','treasury newsletter','analytics','rating']):continue
 if not any(k in low for k in ['annual report','financial statement','financial results','interim','half year','quarter','results','report']):continue
 if not any(k in href.lower() for k in ['.pdf','download','uploads','media','document']):continue
 if title.lower() in ('download','view','download report',''):
  title=re.sub(r'[_-]+',' ',href.rsplit('/',1)[-1].split('?',1)[0].replace('.pdf','')).strip()
 if href not in [r['url'] for r in out]:out.append({'title':title,'url':href,'filename':href.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'bk_group_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
