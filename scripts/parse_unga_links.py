# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
BASE='https://unga-group.com'
archive_pages=[BASE+'/download-category/annual-reports-and-financial-statements/']+[BASE+f'/download-category/annual-reports-and-financial-statements/page/{n}/' for n in (2,3)]
headers={'User-Agent':'Mozilla/5.0'}
s=requests.Session();s.headers.update(headers)
records=[]
for p in archive_pages:
    fp=PROJECT_ROOT / ('unga_annual_reports.html' if p.endswith('/statements/') else 'unga_annual_reports_p'+p.rstrip('/').split('/')[-1]+'.html')
    html=fp.read_text(errors='ignore') if fp.exists() else s.get(p,timeout=30).text
    soup=BeautifulSoup(html,'html.parser')
    for a in soup.find_all('a',href=True):
        href=urljoin(p,a['href']);text=' '.join(a.get_text(' ',strip=True).split())
        low=(href+' '+text).lower()
        if '/download/' not in href or '/download-category/' in href:continue
        if any(k in low for k in ['agm','governance','policy','circular','director','appointment','insider','dividend','proxy','notice','announcement','code-of-conduct']):continue
        if not any(k in low for k in ['annual','financial','result','statement','report','half','six-month','quarter','h1','q1','q2','q3','q4','202']):continue
        if href in {r['source_page_url'] for r in records}:continue
        try:
            r=s.get(href,timeout=30); r.raise_for_status()
            asoup=BeautifulSoup(r.text,'html.parser')
            dl=asoup.select_one('a.inddl[href]')
            if not dl:
                dl=next((x for x in asoup.find_all('a',href=True) if '.pdf' in x['href'].lower()),None)
            if not dl:continue
            direct=urljoin(href,dl['href'])
            file_title=' '.join((asoup.select_one('h1').get_text(' ',strip=True) if asoup.select_one('h1') else text).split())
            filename=direct.split('filename=')[-1].split('&')[0] if 'filename=' in direct else direct.rsplit('/',1)[-1]
            records.append({'title':file_title or text,'source_page_url':href,'url':direct,'filename':filename})
        except Exception as e:
            print('SKIP',href,e)
with open(str(PROJECT_ROOT / 'unga_report_links.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['title','source_page_url','url','filename']);w.writeheader();w.writerows(records)
print('records',len(records))
for r in records:print(r['title'],'|',r['source_page_url'],'|',r['url'])
