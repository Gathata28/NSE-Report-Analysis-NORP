# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'serena_governance.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.serenahotels.com/about-us/governance',a['href'])
 title=' '.join(a.get_text(' ',strip=True).split())
 low=(title+' '+href).lower()
 if 'document-tc.galaxy.tf' not in href.lower():continue
 if any(k in low for k in ['agm','notice','proxy','poll','resolution','question','answer','minutes','board','appointment','circular','governance','policy','press release','announcement']):continue
 if not any(k in low for k in ['annual','financial','result','statement','half-year','half year','interim','report','abridged']):continue
 if not title:title=re.sub(r'[_-]+',' ',href.rsplit('/',1)[-1].replace('.pdf','')).strip()
 if href not in [r['url'] for r in out]:out.append({'title':title,'url':href,'filename':href.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'tpse_serena_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
