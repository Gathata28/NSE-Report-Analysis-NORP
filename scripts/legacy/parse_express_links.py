# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'expresskenya.co.ke_investor-relations__1787826096054.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://expresskenya.co.ke/investor-relations/',a['href'])
 title=(a.get('aria-label') or a.get_text(' ',strip=True) or '').strip()
 title=' '.join(title.split())
 low=(href+' '+title).lower()
 if any(k in low for k in ['agm','proxy','polling','governance','policy','cautionary','rights offer','resignation','appointment','director','notice','calendar','question','answer','minutes']):continue
 if not any(k in low for k in ['financial','annual report','interim','half year','half-year','quarter','results','statement']):continue
 if not ('.pdf' in href.lower() or '/uploads/' in href.lower() or '/static/' in href.lower()):continue
 if not title or title.lower() in ('view file','download','download file'):
  title=re.sub(r'[_-]+',' ',href.rsplit('/',1)[-1].split('?',1)[0].replace('.pdf','')).strip()
 if href not in [r['url'] for r in out]:out.append({'title':title,'url':href,'filename':href.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'express_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
