# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
path=Path(str(PROJECT_ROOT / 'data' / 'sources' / 'www.eaagads.co.ke_annual-reports-and-financial-statements__1787825744366.html'))
soup=BeautifulSoup(path.read_text(errors='ignore'),'html.parser')
out=[]
for a in soup.find_all('a',href=True):
 href=urljoin('https://www.eaagads.co.ke/annual-reports-and-financial-statements/',a['href'])
 text=' '.join(a.get_text(' ',strip=True).split())
 low=(href+' '+text).lower()
 if any(x in low for x in ['agm','polling','proxy','notice','minutes','policy','governance','charter']):continue
 if not any(x in low for x in ['.pdf','.xlsx','.xls','.doc','annual','financial','report','result']):continue
 if text.lower() not in ('download file','download','download pdf'):
  continue
 parent=a.parent
 container=parent.parent if parent else None
 title=' '.join(container.get_text(' ',strip=True).split()) if container else ''
 m=re.search(r'(ANNUAL REPORT AND FINANCIAL STATEMENTS FOR THE YEAR ENDED 31 MARCH \d{4})',title,re.I)
 if m:title=m.group(1).title()
 else:title='Eaagads annual financial statements '+(re.search(r'20\d{2}',href).group(0) if re.search(r'20\d{2}',href) else '')
 if href not in [r['url'] for r in out]:out.append({'title':title,'url':href,'filename':href.rsplit('/',1)[-1]})
with open(str(PROJECT_ROOT / 'eaagads_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename']);w.writeheader();w.writerows(out)
print('records',len(out))
for r in out:print(r)
