# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
INDEX=Path(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'))
rows=list(csv.DictReader(INDEX.open(encoding='utf-8')));existing={(r['issuer'],r['download_url']) for r in rows};new=0
for x in csv.DictReader(open(str(PROJECT_ROOT / 'centum_annual_report_links.csv'),encoding='utf-8')):
 title=x['title'];url=x['url'];low=(title+' '+url).lower()
 if 'hy2016' in low or 'interim' in low or 'half' in low:freq='Semi-annual / half-year'
 else:freq='Annual / full-year'
 subtype='Results booklet / abridged report' if 'abridged' in low else ('Financial results / statements' if 'financial statement' in low else 'Annual report')
 years=re.findall(r'20\d{2}',title+' '+url);year=years[0] if years else ''
 if '2014/2015' in low:year='2015'
 if '2013/2014' in low:year='2014'
 if '2012/2013' in low:year='2013'
 if '2011/2012' in low:year='2012'
 if '2010/2011' in low:year='2011'
 if '2009/2010' in low:year='2010'
 if '2008/2009' in low:year='2009'
 if '2007/2008' in low:year='2008'
 if '2006/2007' in low:year='2007'
 if '2003/2004' in low:year='2004'
 if '2002/2003' in low:year='2003'
 if not year:continue
 key=('Centum Investment Company PLC',url)
 if key in existing:continue
 rows.append({'record_id':'','issuer':'Centum Investment Company PLC','ticker':'CTUM','report_frequency':freq,'document_subtype':subtype,'report_year_label':year,'webpage_title':title,'source_page_url':'https://centum.co.ke/annual-reports/','download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from .pdf URL)','source_tier':'Issuer website'});existing.add(key);new+=1
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier']
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
with INDEX.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('total',len(rows),'added',new)
