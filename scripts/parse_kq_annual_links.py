# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'kq_annual_reports.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://corporate.kenya-airways.com/en/investors-shareholders/annual-reports/',a['href'])
 if '.pdf' not in href.lower():continue
 low=href.lower();text=' '.join(a.get_text(' ',strip=True).split())
 filename=href.rsplit('/',1)[-1]
 itemlow=(filename+' '+text).lower()
 if 'annual' not in itemlow:continue
 if any(k in itemlow for k in ['agm','proxy','poll','notice','circular','governance','shareholder','general meeting','press-release']):continue
 # Locate nearest meaningful title in the report card.
 card=a.find_parent(['li','article','div'])
 ctext=' '.join((card or a).get_text(' ',strip=True).split())
 title=text.strip() or ' '.join(s.get_text(' ',strip=True) for s in a.find_all('span')).strip() or filename
 if not title or title.lower() in ('download pdf','view pdf'):title=filename
 date=''
 m=re.search(r'\b\d{1,2}\s+[A-Za-z]{3}\s+20\d{2}\b',ctext)
 if m:date=m.group(0)
 if href not in {x['url'] for x in out}:out.append({'title':title,'url':href,'publication_date':date})
with open(str(PROJECT_ROOT / 'kq_annual_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','publication_date']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
