# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv, json, re, requests
from pathlib import Path

out = []

def add(issuer, ticker, page_title, page_url, title, url, source_tier='Issuer website'):
    t = title.strip()
    low = t.lower()
    if not any(k in low for k in ['annual report','integrated report','financial statements','financial statement','results booklet','results presentation','press release','press commentary','interim','half year','h1','q1','q2','q3','q4']):
        return
    report_year = ''
    for m in re.finditer(r'(20\d{2}|FY\s?\d{2}|HY\s?\d{2}|H1\s?\d{2})', t, re.I):
        report_year = m.group(1)
        if report_year.startswith('20'): break
    if 'annual report' in low or 'integrated report' in low or 'fy' in low and 'results' in low:
        freq = 'Annual / full-year'
    elif any(x in low for x in ['half year','h1','hy','interim']):
        freq = 'Semi-annual / half-year'
    elif re.search(r'\bq[1-4]\b', low):
        freq = 'Quarterly'
    else:
        freq = 'Periodic results material'
    subtype = 'PDF report'
    if 'presentation' in low: subtype='Investor presentation'
    elif 'booklet' in low: subtype='Results booklet'
    elif 'press release' in low or 'commentary' in low: subtype='Results announcement/commentary'
    elif 'financial statement' in low or 'financial statements' in low: subtype='Financial statements'
    status='unchecked'
    ctype=''
    try:
        r=requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, stream=True, timeout=30, allow_redirects=True)
        status=str(r.status_code)
        ctype=r.headers.get('content-type','')
        r.close()
    except Exception as e:
        status='error:'+type(e).__name__
    out.append({'issuer':issuer,'ticker':ticker,'report_frequency':freq,'document_subtype':subtype,'report_year_label':report_year,'webpage_title':page_title,'source_page_url':page_url,'download_url':url,'http_status':status,'content_type':ctype,'source_tier':source_tier})

# Safaricom annual archive
for r in csv.DictReader(open(str(PROJECT_ROOT / 'safaricom_annual_links.csv'),encoding='utf-8')):
    if re.search(r'\b20\d{2} Annual Report\b', r['link_text'], re.I) and r['direct_url'].lower().endswith('.pdf'):
        add('Safaricom PLC','SCOM','Safaricom - Annual Reports | Full Year & Half Year Reports','https://www.safaricom.co.ke/investor-relations-landing/reports/annual-reports',r['link_text'],r['direct_url'])
# Safaricom periodic results
for r in csv.DictReader(open(str(PROJECT_ROOT / 'safaricom_results_links.csv'),encoding='utf-8')):
    if re.search(r'\b(FY|H1)\d{2}\b', r['link_text'], re.I) and r['direct_url'].lower().endswith('.pdf'):
        add('Safaricom PLC','SCOM','Safaricom Financial Reports','https://www.safaricom.co.ke/investor-relations-landing/reports/financial-report/financial-results',r['link_text'],r['direct_url'])
# Equity primary page; exclude board/governance documents
for r in csv.DictReader(open(str(PROJECT_ROOT / 'issuer_archive_links_sample.csv'),encoding='utf-8')):
    if r['issuer_context']=='Equity Group' and not re.search(r'board|committee|charter|governance|risk|policy|tor',r['link_text'],re.I):
        add('Equity Group Holdings PLC','EQTY','Equity Group | Investor Relations','https://equitygroupholdings.com/investor-relations/',r['link_text'],r['direct_url'])
# KCB primary page persisted from browser evaluation
for r in json.load(open(str(PROJECT_ROOT / 'kcb_financial_links_full.json'),encoding='utf-8')):
    add('KCB Group PLC','KCB','Financial Statements | KCB Bank','https://kcbgroup.com/financial-statements',r['text'],r['href'])
# dedupe by issuer and URL
seen=set(); dedup=[]
for r in out:
    key=(r['issuer'],r['download_url'])
    if key not in seen:
        seen.add(key); r['record_id']=f"NSE-{len(dedup)+1:05d}"; dedup.append(r)
out=dedup
fields=list(out[0].keys()) if out else []
with open(str(PROJECT_ROOT / 'nse_first_party_tranche_index.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
print('records',len(out))
from collections import Counter
print('issuers',Counter(r['issuer'] for r in out))
print('status',Counter(r['http_status'] for r in out))
