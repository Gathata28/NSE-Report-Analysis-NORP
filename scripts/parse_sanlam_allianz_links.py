# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'ke.sanlamallianz.com_life-insurance_about_our-profile_investor-relations_1787826434286.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for table in soup.find_all('table'):
 for tr in table.find_all('tr'):
  cells=tr.find_all('td')
  if len(cells)<2:continue
  title=' '.join(cells[0].get_text(' ',strip=True).split())
  a=cells[-1].find('a',href=True)
  if not a:continue
  href=urljoin('https://ke.sanlamallianz.com/life-insurance/about/our-profile',a['href'])
  low=(title+' '+href).lower()
  if any(k in low for k in ['agm','proxy','polling','minutes','question','resolution','rights issue','information memorandum','policy','cautionary','appointment','chairman','calendar','unit trust','no objection','high court','approval letter','press release']):continue
  if not any(k in low for k in ['annual report','integrated report','financial statements','financial results','interim results','unaudited results','audited results']):continue
  if not any(k in href.lower() for k in ['.pdf','download','uploads','media']):continue
  if href not in [r['url'] for r in out]:out.append({'title':title,'url':href,'filename':href.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'sanlam_allianz_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
