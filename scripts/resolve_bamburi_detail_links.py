# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,requests,re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
base='https://bamburigroup.com'
seed=[]
with open(str(PROJECT_ROOT / 'bamburi_report_links.csv'),encoding='utf-8') as f:
 for r in csv.DictReader(f):
  if r['url'].startswith(base+'/') and r['url'].rstrip('/') != 'https://bamburigroup.com/bamburi-cement-investor-relations/annual-reports' and not r['url'].lower().endswith('.pdf') and 'annual-report' in (r['url']+' '+r['title']).lower():seed.append(r)
out=[]
for r in seed:
 try:html=requests.get(r['url'],headers={'User-Agent':'Mozilla/5.0'},timeout=20).text
 except Exception as e:print('ERROR',r['url'],e);continue
 soup=BeautifulSoup(html,'html.parser')
 found=False
 for a in soup.find_all('a',href=True):
  href=urljoin(r['url'],a['href']); t=' '.join((a.get_text(' ',strip=True) or a.get('title','')).split()); low=(href+' '+t).lower()
  if '.pdf' not in href.lower():continue
  if any(k in low for k in ['agm','proxy','polling','notice','governance','policy','shareholder']):continue
  if not any(k in low for k in ['annual','financial','report','result','statement','half','interim']):continue
  out.append({'title':r['title'],'url':href,'filename':href.rsplit('/',1)[-1],'source_page':r['url']});found=True
 if not found:print('NO_PDF',r['title'],r['url'])
# also preserve direct PDF found on archive page
for r in csv.DictReader(open(str(PROJECT_ROOT / 'bamburi_report_links.csv'),encoding='utf-8')):
 if '.pdf' in r['url'].lower() and r['url'] not in [x['url'] for x in out]:
  title='Bamburi Cement Financial Statements 2025' if r['title']=='IMPACT' else r['title']
  out.append({'title':title,'url':r['url'],'filename':r['filename'],'source_page':'https://bamburigroup.com/bamburi-cement-investor-relations/annual-reports/'})
seen=set();clean=[]
for r in out:
 if r['url'] not in seen:clean.append(r);seen.add(r['url'])
with open(str(PROJECT_ROOT / 'bamburi_report_links_resolved.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename','source_page']);w.writeheader();w.writerows(clean)
print('records',len(clean))
for r in clean:print(r)
