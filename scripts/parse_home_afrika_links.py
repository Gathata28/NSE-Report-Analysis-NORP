# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.homeafrika.com_investor-info_annual-reports_1787825903363.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for row in soup.select('table.annual-table tr'):
 cells=row.find_all('td')
 if len(cells)<4:continue
 title=' '.join(cells[0].get_text(' ',strip=True).split())
 desc=' '.join(cells[1].get_text(' ',strip=True).split())
 report_date=' '.join(cells[2].get_text(' ',strip=True).split())
 a=cells[3].find('a',href=True)
 if not a:continue
 url=urljoin('https://www.homeafrika.com/investor-info/annual-reports',a['href'])
 low=(title+' '+desc+' '+url).lower()
 if any(k in low for k in ['agm','polling','proxy','notice','minutes','governance','policy','charter']):continue
 if not any(k in low for k in ['annual','financial','report','result','publication','interim','quarter']):continue
 if url not in [r['url'] for r in out]:out.append({'title':title,'description':desc,'report_date':report_date,'url':url,'filename':url.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'home_afrika_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','description','report_date','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
