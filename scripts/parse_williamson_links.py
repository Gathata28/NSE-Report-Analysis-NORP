# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'williamson_investor_reports.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.williamsontea.com/investor-reports/',a['href']);fn=href.rsplit('/',1)[-1]
 if '.pdf' not in href.lower():continue
 title=' '.join(a.get_text(' ',strip=True).split());low=(title+' '+fn).lower()
 if any(k in low for k in ['agm','poll','notice','resolution','advert','invitation','proxy','circular','agenda','minutes']):continue
 if not any(k in low for k in ['annual','financial','account','half','result','press','fs','statement']):continue
 issuer='Kapchorua Tea Company PLC' if 'kapchorua' in low or re.search(r'\bkap\b',low) else 'Williamson Tea Kenya PLC'
 ticker='KAPC' if issuer.startswith('Kapchorua') else 'WTK'
 if title.lower() in ('download','download pdf','pdf',''):
  title=re.sub(r'[_-]+',' ',fn.rsplit('?',1)[0].replace('.pdf','')).strip()
 if href not in {r['url'] for r in out}:out.append({'issuer':issuer,'ticker':ticker,'title':title,'url':href})
with open(str(PROJECT_ROOT / 'williamson_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['issuer','ticker','title','url']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
