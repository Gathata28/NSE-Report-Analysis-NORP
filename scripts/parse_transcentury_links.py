# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,requests,re,urllib3
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base='https://www.transcentury.co.ke'
main=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.transcentury.co.ke_annual-reports_1787827088194.html'))
soup=BeautifulSoup(main.read_text(errors='ignore'),'html.parser')
seeds=[{'title':'TransCentury 2023 Integrated Report','url':base+'/post/transcentury-2023-integrated-report'},{'title':'TransCentury 2022 Integrated Report','url':base+'/post/transcentury-2022-integrated-report'},{'title':'TransCentury 2021 Integrated Report','url':base+'/post/transcentury-2021-integrated-report'}]
out=[]
for r in seeds:
 try:html=requests.get(r['url'],headers={'User-Agent':'Mozilla/5.0'},timeout=25,verify=False).text
 except Exception as e:print('ERROR',r['url'],e);continue
 s=BeautifulSoup(html,'html.parser')
 for a in s.find_all('a',href=True):
  u=urljoin(r['url'],a['href']);low=(u+' '+a.get_text(' ',strip=True)).lower()
  if '.pdf' not in u.lower():continue
  if any(k in low for k in ['agm','proxy','polling','notice','governance','policy','circular']):continue
  out.append({'title':r['title'],'url':u,'filename':u.rsplit('/',1)[-1],'source_page':r['url']})
# include any report-like PDF links directly on archive snapshot
for a in soup.find_all('a',href=True):
 u=urljoin(base+'/annual-reports',a['href']);t=' '.join((a.get_text(' ',strip=True) or a.get('title','')).split());low=(u+' '+t).lower()
 if '.pdf' in u.lower() and any(k in low for k in ['annual','financial','integrated','report','result']):out.append({'title':t,'url':u,'filename':u.rsplit('/',1)[-1],'source_page':base+'/annual-reports'})
seen=set();clean=[]
for r in out:
 if r['url'] not in seen:clean.append(r);seen.add(r['url'])
with open(str(PROJECT_ROOT / 'transcentury_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename','source_page']);w.writeheader();w.writerows(clean)
print('records',len(clean))
for r in clean:print(r)
