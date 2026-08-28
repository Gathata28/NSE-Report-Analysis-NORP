# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'bat_reports.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.batkenya.com/investors-and-reporting/financial-sustainability-reports',a['href'])
 if '.pdf' not in href.lower():continue
 fn=href.rsplit('/',1)[-1]
 low=fn.lower()
 if '/annual-reports/' in href.lower() and 'annual' in low:kind='Annual report'
 elif '/financial-statements/' in href.lower() and any(k in low for k in ['full-year','half-year','financial','results']):kind='Financial results / statements'
 else:continue
 title=' '.join(a.get_text(' ',strip=True).split()) or fn
 out.append({'title':title,'url':href,'kind':kind,'filename':fn})
seen=set();dedup=[]
for r in out:
 if r['url'] not in seen:seen.add(r['url']);dedup.append(r)
with open(str(PROJECT_ROOT / 'bat_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','kind','filename']);w.writeheader();w.writerows(dedup)
print('records',len(dedup))
for r in dedup:print(r)
