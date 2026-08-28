# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
from pathlib import Path
root=Path(str(PROJECT_ROOT))
current=list(csv.DictReader(open(root/'current_nse_universe.csv',encoding='utf-8')))
by_ticker={r['ticker'].strip().upper():r for r in current}
known_sectors={'AGRICULTURAL','AUTOMOBILES & ACCESSORIES','BANKING','COMMERCIAL & SERVICES','CONSTRUCTION & ALLIED','ENERGY & PETROLEUM','INVESTMENT','INSURANCE','MANUFACTURING & ALLIED'}
aliases={'eaagads ltd.':'EGAD','hf group plc.':'HFCK','britam holdings plc.':'BRIT','stanbic holdings ltd.':'SBIC','i & m holdings plc.':'IMH','kcb group plc.':'KCB','standard chartered bank kenya ltd.':'SCBK','equity group holdings plc.':'EQTY','britam holdings plc.':'BRITAM','kapchorua tea kenya plc.':'KAPC','kakuzi plc':'KUKZ','limuru tea co. ltd.':'LIMT','sasini plc.':'SASN','williamson tea kenya plc.':'WTK','car & general (k) ltd.':'CGEN','express kenya plc.':'XPRS','kenya airways ltd.':'KQ','nation media group plc.':'NMG','standard group plc.':'SGL','tps eastern africa (serena) ltd.':'TPSE','wpp scangroup plc.':'SCAN','uchumi supermarket plc.':'UCHM','eveready east africa ltd..':'EVRD','longhorn publishers plc.':'LKL','deacons (east africa) plc.':'DCON','sameer africa plc.':'SMER','nairobi business ventures ltd':'NBV','homeboyz entertainment plc':'HBE','arm cement plc':'ARM','bamburi cement ltd':'BAMB','crown paints kenya plc':'CRWN','e.a cables ltd':'CABL','e.a portland cement ltd':'PORT','total kenya ltd.':'TOTL','kengen plc':'KEGN','kenya power & lighting plc':'KPLC','umeme ltd':'UMME','olympia capital holdings ltd':'OCH','centum investment plc':'CTUM','trans - century plc.':'TCL','home afrika ltd.':'HAFR','kurwitu ventures ltd':'KURV','jubilee holdings ltd':'JUB','sanlam kenya plc':'SLAM','kenya re - insurance corporation ltd':'KNRE','liberty kenya holdings':'LBTY','britam holdings plc.':'BRIT','nairobi securities exchange plc':'NSE','b.o.c kenya plc.':'BOC','british american tobacco kenya plc':'BAT','carbacid investments plc':'CARB','east african breweries ltd':'EABL','mumias sugar co. ltd':'MSC','unga group ltd':'UNGA','kenya orchards ltd':'ORCH'}
text=Path(root/'cdsc_listed_companies_text.txt').read_text(errors='ignore').splitlines()
parsed=[];await_sector=False;sector=None
for raw in text:
 line=' '.join(raw.strip().split())
 if not line:continue
 if line=='LISTED COMPANIES':await_sector=True;sector=None;continue
 if await_sector and line in known_sectors:
  sector=line;await_sector=False;continue
 if sector is None:continue
 if line.isupper() and line not in known_sectors:sector=None;await_sector=False;continue
 if line in ('Home','Listed Companies') or len(line)>80:continue
 if re.search(r'\b(Phone|Email|Contact|Careers|Services|Links|About us|©|All rights)\b',line,re.I):continue
 if line.lower().startswith(('download','investor','corporate')):continue
 parsed.append((sector,line))
seen=set();records=[]
for sector,name in parsed:
 key=name.lower()
 if key in seen:continue
 seen.add(key)
 ticker=aliases.get(key,'')
 if not ticker:
  norm=re.sub(r'[^a-z0-9]','',key)
  best=None
  for r in current:
   cn=r['issuer_name'].lower();cnorm=re.sub(r'[^a-z0-9]','',cn)
   if norm and (norm in cnorm or cnorm in norm):best=r;break
  if best:ticker=best['ticker']
 matches=[r for r in current if r.get('ticker','').strip().upper()==ticker]
 if len(matches)>1:
  nt=set(re.findall(r'[a-z0-9]+',key))-{'ltd','plc','ord','kenya','co'}
  cu=max(matches,key=lambda r:len(nt & set(re.findall(r'[a-z0-9]+',r.get('issuer_name','').lower()))))
 else:cu=matches[0] if matches else by_ticker.get(ticker)
 status='Current NSE page' if cu else 'Absent from current 66-row NSE page; historical candidate'
 records.append({'legal_or_display_name':name,'ticker':ticker,'sector':sector,'isin':cu.get('isin','') if cu else '','status_as_of_2026-08-27':status,'status_source_url':'https://www.nse.co.ke/listed-companies/' if cu else 'https://cdsckenya.com/listed-companies/','former_official_site':'','last_known_listing_or_disclosure_period':'','archive_coverage_status':'See report index; historical status and completeness require issuer/NSE/CMA confirmation','notes':'Name enumerated from official CDSC listed-companies page; absence from current NSE page is not by itself proof of delisting.'})
for name,ticker in [('Athi River Mining / ARM Cement','ARM'),('Mumias Sugar Co. Ltd','MSC'),('Uchumi Supermarket Plc','UCHM'),('Deacons (East Africa) Plc','DCON'),('Homeboyz Entertainment Plc','HBE'),('Kenya Orchards Limited','ORCH')]:
 if not any(r['ticker']==ticker for r in records):records.append({'legal_or_display_name':name,'ticker':ticker,'sector':'','isin':by_ticker.get(ticker,{}).get('isin',''),'status_as_of_2026-08-27':'Historical candidate; requires status-source confirmation','status_source_url':'https://www.nse.co.ke/our-story/','former_official_site':'','last_known_listing_or_disclosure_period':'','archive_coverage_status':'Historical issuer universe gap','notes':'Seeded from prior working leads, not claimed as a complete authoritative delisting list.'})
secondary_status_lead='https://www.african-markets.com/en/stock-markets/nse/cma-pledges-to-delist-hutchings-biemer-a-baumann-from-nairobi-securities-exchange'
for name,ticker in [('Hutchings Biemer Ltd','HBL'),('A. Baumann Ltd','BAUM'),('CMC Holdings Ltd','CMC'),('Rea Vipingo Ltd','REA')]:
 if not any(r['ticker']==ticker for r in records):records.append({'legal_or_display_name':name,'ticker':ticker,'sector':'','isin':'','status_as_of_2026-08-27':'Historical candidate; secondary status lead only','status_source_url':secondary_status_lead,'former_official_site':'','last_known_listing_or_disclosure_period':'','archive_coverage_status':'Historical issuer universe gap','notes':'Named in a secondary report quoting CMA/NSE history; primary NSE/CMA status notice not yet located. Do not infer delisting from this lead alone.'})
secondary_discovery='https://en.wikipedia.org/wiki/Companies_traded_on_the_Nairobi_Securities_Exchange'
for name,ticker in [('Atlas Development & Support Services Ltd','ADSS'),('Stanlib Fahari I-REIT','FAHR')]:
 if not any(r['ticker']==ticker for r in records):records.append({'legal_or_display_name':name,'ticker':ticker,'sector':'','isin':'','status_as_of_2026-08-27':'Historical candidate; secondary discovery lead only','status_source_url':secondary_discovery,'former_official_site':'','last_known_listing_or_disclosure_period':'','archive_coverage_status':'Historical issuer universe gap','notes':'Named in a historical company-list discovery source; primary NSE/CMA listing and exit/status notice not yet located. Do not infer delisting from this lead alone.'})
fields=list(records[0].keys())
with open(root/'historical_nse_universe.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
print('records',len(records),'current_matches',sum(r['status_as_of_2026-08-27']=='Current NSE page' for r in records),'historical_candidates',sum('historical' in r['status_as_of_2026-08-27'].lower() or 'absent' in r['status_as_of_2026-08-27'].lower() for r in records))
