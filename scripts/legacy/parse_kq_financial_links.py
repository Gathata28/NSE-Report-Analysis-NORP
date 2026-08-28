# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
soup=BeautifulSoup(Path(str(PROJECT_ROOT / 'kq_financial_results.html')).read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://corporate.kenya-airways.com/en/investors-shareholders/financial-results/',a['href'])
 if '.pdf' not in href.lower():continue
 filename=href.rsplit('/',1)[-1]
 text=' '.join(a.get_text(' ',strip=True).split()).strip()
 itemlow=(filename+' '+text).lower()
 if any(k in itemlow for k in ['profit-warning','profit warning','agm','proxy','poll','notice','governance','shareholder']):continue
 if not any(k in itemlow for k in ['financial','result','statement','half','six-month','quarter','h1','q1','q2','q3','q4','fy-','full-year','auditor','chairman','investor-briefing']):continue
 title=text or filename
 # Prefer a readable filename-derived title when the anchor contains no label.
 if not title or title.lower() in ('download pdf','view pdf','pdf'):title=filename
 out.append({'title':title,'url':href,'filename':filename})
seen=set();dedup=[]
for r in out:
 if r['url'] not in seen:seen.add(r['url']);dedup.append(r)
with open(str(PROJECT_ROOT / 'kq_financial_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(dedup)
print('records',len(dedup))
for r in dedup:print(r)
