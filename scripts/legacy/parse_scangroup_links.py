# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'scangroup_investor_relations.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://wpp-scangroup.com/investor-relations/',a['href']);fn=href.rsplit('/',1)[-1]
 if '.pdf' not in href.lower():continue
 title=' '.join(a.get_text(' ',strip=True).split());low=(title+' '+fn).lower()
 if any(k in low for k in ['agm','annual-general','proxy','resolution','polling','voting','sustainability','policy','governance','board','director','registrar','appointment','resignation','cautionary','profit-warning','warning','stakeholder','rights-issue','minorities','change-of']):continue
 if not any(k in low for k in ['annual','financial','result','half','interim','q1','q2','q3','q4','publication','abridged','statement']):continue
 if title.lower() in ('download','download pdf','view pdf','pdf',''):
  title=re.sub(r'[_-]+',' ',fn.rsplit('?',1)[0].replace('.pdf','')).strip()
 if href not in {r['url'] for r in out}:out.append({'title':title,'url':href,'filename':fn})
with open(str(PROJECT_ROOT / 'scangroup_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
