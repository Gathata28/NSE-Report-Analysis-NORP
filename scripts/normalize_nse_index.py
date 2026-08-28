# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re,hashlib,os,urllib.parse
from pathlib import Path
from datetime import date
root=Path(str(PROJECT_ROOT))
master=root/'nse_first_party_tranche_index.csv'
out=root/'nse_reports_normalized.csv'
current=list(csv.DictReader((root/'current_nse_universe.csv').open(encoding='utf-8')))
by_ticker={r.get('ticker','').strip().upper():r for r in current}
by_name={r.get('issuer name','').strip().lower():r for r in current}
manifest=[]
mp=root/'verified_download_manifest.csv'
if mp.exists():manifest=list(csv.DictReader(mp.open(encoding='utf-8')))
# Exact basename matching is conservative and avoids attributing a checksum to the wrong URL.
manifest_by_base={}
for m in manifest:
    b=os.path.basename(m.get('path','')).lower()
    if b:manifest_by_base[b]=m

def infer_title(r):
    t=(r.get('document_title') or r.get('webpage_title') or '').strip()
    if t and t.lower() not in ('investor relations','download','pdf'): return t
    u=urllib.parse.unquote((r.get('download_url') or '').split('?',1)[0])
    return os.path.basename(u).replace('_',' ').replace('-',' ').strip()

def infer_period_end(r,title):
    text=(title+' '+r.get('download_url','')).lower()
    # Only populate when the period end is explicitly stated or reliably encoded.
    patterns=[(r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(20\d{2})',None),
              (r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(20\d{2})',None)]
    months={'january':'01','february':'02','march':'03','april':'04','may':'05','june':'06','july':'07','august':'08','september':'09','october':'10','november':'11','december':'12'}
    m=re.search(patterns[0][0],text)
    if m:return f'{m.group(3)}-{months[m.group(2)]}-{int(m.group(1)):02d}'
    m=re.search(patterns[1][0],text)
    if m:return f'{m.group(2)}-{months[m.group(1)]}'
    if '30 june' in text or 'june 30' in text:return re.search(r'20\d{2}',text).group(0)+'-06-30' if re.search(r'20\d{2}',text) else ''
    if '31 march' in text or 'march 31' in text:return re.search(r'20\d{2}',text).group(0)+'-03-31' if re.search(r'20\d{2}',text) else ''
    if '30 september' in text or 'september 30' in text:return re.search(r'20\d{2}',text).group(0)+'-09-30' if re.search(r'20\d{2}',text) else ''
    if '31 december' in text or 'december 31' in text:return re.search(r'20\d{2}',text).group(0)+'-12-31' if re.search(r'20\d{2}',text) else ''
    return ''

def find_manifest(r):
    u=urllib.parse.unquote((r.get('download_url') or '').split('?',1)[0]).lower()
    candidates=[os.path.basename(u)]
    q=urllib.parse.parse_qs(urllib.parse.urlsplit(r.get('download_url','')).query)
    candidates += [os.path.basename(urllib.parse.unquote(v)) for v in q.get('filename',[])]
    for c in candidates:
        if c in manifest_by_base:return manifest_by_base[c]
    return None

rows=[]
for r in csv.DictReader(master.open(encoding='utf-8')):
    title=infer_title(r)
    freq=r.get('report_frequency','').strip()
    subtype=r.get('document_subtype','').strip()
    low=(title+' '+subtype).lower()
    core='Yes' if subtype in ('Annual report','Financial results / statements') else 'No'
    if any(k in low for k in ['presentation','briefing','press release','commentary','booklet','abridged','infograph']):core='No'
    ticker=r.get('ticker','').strip().upper()
    cu=by_ticker.get(ticker)
    if not cu:cu=by_name.get(r.get('issuer','').strip().lower())
    listing_status=(cu.get('status','Current NSE universe') if cu else 'Historical / not in current 66-row universe')
    raw_status=str(r.get('http_status','')).strip()
    if raw_status in ('200','200 verified'):link_status='HTTP 200 verified'
    elif raw_status in ('403','404','500','502','503'):link_status=f'HTTP {raw_status} recorded; issuer-page linkage retained'
    elif 'linked from issuer page' in raw_status:link_status='Linked from official issuer page; direct HTTP validation pending'
    else:link_status=raw_status or 'Not validated'
    m=find_manifest(r)
    dedupe=hashlib.sha256('|'.join([r.get('issuer','').strip().lower(),r.get('report_year_label','').strip(),freq,subtype]).encode()).hexdigest()[:16]
    row=dict(r)
    row.update({'document_title':title,'report_period_end':infer_period_end(r,title),'publication_date':r.get('publication_date',''),'core_report_flag':core,'listing_status':listing_status,'validation_date':'2026-08-27' if raw_status in ('200','200 verified') else '', 'link_verification_status':link_status,'validation_method':'HTTP GET' if raw_status in ('200','200 verified') else ('official source-page link capture' if 'linked from issuer page' in raw_status else ''),'local_file':m.get('path','') if m else '','local_bytes':m.get('bytes','') if m else '','sha256':m.get('sha256','') if m else '','dedupe_group':dedupe,'collection_date':'2026-08-27','notes':''})
    rows.append(row)
fields=['record_id','issuer','ticker','listing_status','report_frequency','document_subtype','core_report_flag','report_year_label','report_period_end','publication_date','document_title','webpage_title','source_page_url','download_url','source_tier','content_type','http_status','link_verification_status','validation_date','validation_method','local_file','local_bytes','sha256','dedupe_group','collection_date','notes']
with out.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('normalized_records',len(rows),'core',sum(r['core_report_flag']=='Yes' for r in rows),'related',sum(r['core_report_flag']=='No' for r in rows),'with_local_checksum',sum(bool(r['sha256']) for r in rows))
