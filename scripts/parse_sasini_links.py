# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re,requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
base='https://sasini.co.ke/downloads/'
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'sasini_downloads.html')).read_text(errors='ignore'),'html.parser')
s=requests.Session();s.headers.update({'User-Agent':'Mozilla/5.0'})
out=[]
for strong in soup.find_all('strong'):
 title=' '.join(strong.get_text(' ',strip=True).split());low=title.lower()
 if not any(k in low for k in ['annual report','financial statement','half year','financial results','full year']):continue
 if any(k in low for k in ['agm','proxy','sustainability','governance']):continue
 row=strong.find_parent('tr') or strong.parent
 dl=row.find('a',attrs={'data-downloadurl':True})
 if not dl:continue
 attach=dl.get('data-downloadurl')
 direct=attach
 if direct and direct not in {x['url'] for x in out}:out.append({'title':title,'source_page_url':attach,'url':direct})
with open(str(PROJECT_ROOT / 'sasini_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','source_page_url','url']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
