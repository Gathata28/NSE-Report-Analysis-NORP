# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re,requests,urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from urllib.parse import urljoin
base='https://www.umeme.co.ug'
urls=[(str(PROJECT_ROOT / 'data' / 'sources' / 'www.umeme.co.ug_investor-relations_reports_136_1787826206805.html'),'https://www.umeme.co.ug/investor-relations/reports/136'),(str(PROJECT_ROOT / 'data' / 'sources' / 'www.umeme.co.ug_investor-relations_reports_1787826168108.html'),'https://www.umeme.co.ug/investor-relations/reports')]
out=[]
for local,page in urls:
 html=open(local,encoding='utf-8',errors='ignore').read()
 soup=BeautifulSoup(html,'html.parser')
 for a in soup.find_all('a',href=True):
  href=urljoin(page,a['href']); title=' '.join((a.get_text(' ',strip=True) or a.get('title','')).split())
  if ' Reports / ' in title:title=title.split(' Reports / ',1)[0].strip()
  low=(href+' '+title).lower()
  if any(k in low for k in ['agm','proxy','notice','appointment','director','profit warning','presentation','governance','policy','legal']):continue
  if not any(k in low for k in ['annual','financial','interim','half','quarter','result','statement','report']):continue
  if not any(k in href.lower() for k in ['.pdf','uploads','download','media']):continue
  if title.lower() in ('download','view','view report','read more',''):
   title=re.sub(r'[_-]+',' ',href.rsplit('/',1)[-1].split('?',1)[0].replace('.pdf','')).strip()
  date=''
  parent=a.parent
  if parent: date=' '.join(parent.get_text(' ',strip=True).split())
  if href not in [r['url'] for r in out]:out.append({'title':title,'url':href,'filename':href.rsplit('/',1)[-1],'source_page':page,'page_context':date})
with open(str(PROJECT_ROOT / 'umeme_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename','source_page','page_context']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
