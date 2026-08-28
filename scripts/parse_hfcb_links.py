# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re,html
from pathlib import Path
from urllib.parse import quote
s=html.unescape(Path(str(PROJECT_ROOT / 'hfcb_investor_relations.html')).read_text(errors='ignore')).replace('\\"','"')
out=[]
def decode(x):
 return x.replace('\\u0026','&').replace('\\u002F','/').replace('\\u002f','/').replace('\\"','"')
def block(key,nextkey):
 a=s.find('"key":"'+key+'"');b=s.find('"key":"'+nextkey+'"',a+1)
 return s[a:b if b>=0 else len(s)]
for key,nextkey,category in [('financials','investor-briefs','financials'),('annual-reports','agm-documents','annual-reports')]:
 b=block(key,nextkey)
 for ym in re.finditer(r'\{"year":(20\d{2}),"documents":\[(.*?)\]\}',b):
  year=ym.group(1);docs=ym.group(2)
  for m in re.finditer(r'\{"name":"(.*?)","file":"(.*?)"\}',docs):
   name=decode(m.group(1));fn=decode(m.group(2))
   path=f'{category}/{year}/{fn}'
   url='https://hfcb.co.ke/api/investor-relations/file?path='+quote(path,safe='/')
   low=name.lower()
   if any(k in low for k in ['agm','proxy','sustainability','policy','rights issue','brief','notice','registrar']):continue
   if url not in {r['url'] for r in out}:out.append({'title':name,'year':year,'category':category,'url':url,'filename':fn})
with open(str(PROJECT_ROOT / 'hfcb_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','year','category','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out[:12]:print(r)
for r in out[-12:]:print(r)
