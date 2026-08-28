from pathlib import Path
import csv, hashlib, json, os, re, sqlite3
from datetime import datetime, timezone
from norp_engine import market_anomaly_flags

BASE = Path(os.environ.get('NORP_ROOT', Path(__file__).resolve().parents[1]))
DB = BASE / 'data' / 'indexes' / 'nse_reports_archive.sqlite'
RAW = BASE / 'data' / 'market_data' / 'raw'
ATTACHMENT = Path(os.environ.get('NORP_ATTACHMENT_ROOT', BASE / 'data' / 'external' / 'attachment_workspace'))
EXTRACTED = ATTACHMENT / 'extracted'
NESTED = ATTACHMENT / 'nested_extracted'
RAW.mkdir(parents=True, exist_ok=True)

LICENSES = {
    '2007-2012': ('https://data.mendeley.com/datasets/5hk4zw32f5/1', 'Wanjawa, Barack. Nairobi Securities Exchange All Stocks Prices 2007-2012. Mendeley Data, version 1, CC BY 4.0.'),
    '2013-2020': ('https://data.mendeley.com/datasets/73rb78pmzw/2', 'Wanjawa, Barack. Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2013-2020. Mendeley Data, version 2, CC BY 4.0.'),
    '2021': ('https://data.mendeley.com/datasets/97hkwn5y3x/4', 'Wanjawa, Barack. Kenya Nairobi Securities Exchange (NSE) Kenya - All Stocks Prices 2021. Mendeley Data, version 4, CC BY 4.0.'),
    '2022': ('https://data.mendeley.com/datasets/jmcdmnyh2s/2', 'Wanjawa, Barack. Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2022. Mendeley Data, version 2, CC BY 4.0.'),
    '2023-2024': ('https://data.mendeley.com/datasets/ss5pfw8xnk/3', 'Wanjawa, Barack. Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2023-2024. Mendeley Data, version 3, CC BY 4.0.'),
    '2025': ('https://data.mendeley.com/datasets/2b63rx67xt/2', 'Wanjawa, Barack. Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2025. Mendeley Data, version 2, CC BY 4.0.'),
    '2026': ('https://data.mendeley.com/datasets/hvmhnp7f9r/1', 'Wanjawa, Barack. Kenya Nairobi Securities Exchange (NSE) All Stocks Prices 2026. Mendeley Data, version 1, CC BY 4.0.'),
}

def release_period(name):
    years = re.findall(r'20\d{2}', name)
    if '2007-2012' in name or ('2007' in name and '2012' in name): return '2007-2012'
    if any(y in name for y in ['2013','2014','2015','2016','2017','2018','2019','2020']): return '2013-2020'
    if '2021' in name: return '2021'
    if '2022' in name: return '2022'
    if '2023' in name or '2024' in name: return '2023-2024'
    if '2025' in name: return '2025'
    if '2026' in name: return '2026'
    return 'unclassified'

def parse_num(value):
    if value is None: return None
    s=str(value).strip().replace(',','').replace('%','')
    if s in {'','-','—','NA','N/A','null','None'}: return None
    try: return float(s)
    except ValueError: return None

def parse_date(value):
    if value is None: return None
    s=str(value).strip()
    for fmt in ('%Y-%m-%d','%d/%m/%Y','%m/%d/%Y','%d-%m-%Y','%Y/%m/%d','%d %b %Y','%d-%b-%Y','%d-%b-%y'):
        try: return datetime.strptime(s,fmt).date().isoformat()
        except ValueError: pass
    return None

def canonical(row, *names):
    for n in names:
        if n in row: return row[n]
    lowered={str(k).strip().lower():v for k,v in row.items()}
    for n in names:
        if n.lower() in lowered: return lowered[n.lower()]
    return None

def dataset_files():
    files=[]
    if EXTRACTED.exists():
        files.extend((p, 'attached_top_level') for p in EXTRACTED.glob('*.csv'))
    if NESTED.exists():
        files.extend((p, 'nested_archive') for p in NESTED.rglob('*.csv'))
    return sorted(files, key=lambda x: str(x[0]))

def safe_name(p):
    return re.sub(r'[^A-Za-z0-9_.-]+','_',p.name)

def source_context(p):
    try: rel=p.relative_to(EXTRACTED); return 'ComprehensiveReviewofNairobiSecuritiesExchangeFiles.zip', str(rel)
    except ValueError: pass
    try: rel=p.relative_to(NESTED); return rel.parts[0]+'.zip', str(Path(*rel.parts[1:]))
    except ValueError: return 'attached_archive', p.name

def main():
    if not DB.exists(): raise FileNotFoundError(f'Missing NORP database: {DB}')
    files=dataset_files()
    if not files: raise FileNotFoundError('No extracted CSV datasets found')
    con=sqlite3.connect(DB); con.execute('PRAGMA foreign_keys=ON'); cur=con.cursor()
    cur.execute('DELETE FROM market_data_anomaly'); cur.execute('DELETE FROM market_sector_classification'); cur.execute('DELETE FROM market_observation'); cur.execute('DELETE FROM market_import_file'); cur.execute('DELETE FROM market_dataset')
    now=datetime.now(timezone.utc).isoformat(); dataset_count=obs_count=sector_count=anomaly_count=0; manifest=[]
    for p, origin in files:
        data=p.read_bytes(); sha=hashlib.sha256(data).hexdigest(); copied=RAW/(sha[:12]+'_'+safe_name(p)); copied.write_bytes(data)
        period=release_period(str(p)); url, attribution=LICENSES.get(period,(None,'License not independently verified from the attached record'))
        rights='cc_by_4_0' if url else 'license_unverified'
        name=f'NSE attached market data — {p.name}'
        archive,rel=source_context(p)
        cur.execute('INSERT INTO market_dataset(dataset_name,original_filename,source_archive,source_relative_path,release_period,source_url,source_title,source_provider,license_name,license_url,attribution,rights_status,source_file_sha256,source_file_bytes,imported_at,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(name,p.name,archive,rel,period,url,'Mendeley Data release' if url else 'Attached CSV without independently confirmed release record','Mendeley Data' if url else 'Attached archive','CC BY 4.0' if url else 'License not independently verified','https://creativecommons.org/licenses/by/4.0/' if url else None,attribution,rights,sha,len(data),now,f'Preserved source origin: {origin}; raw file copied to {copied.relative_to(BASE)}'))
        did=cur.lastrowid; dataset_count+=1
        with p.open(newline='',encoding='utf-8-sig',errors='replace') as f:
            reader=csv.DictReader(f); headers=reader.fieldnames or []; rows=0; is_sector=any(h.lower() in {'sector','stock_code','stock_name'} for h in headers)
            for rownum,row in enumerate(reader, start=2):
                rows+=1; raw=json.dumps(row,ensure_ascii=False,sort_keys=True)
                if is_sector:
                    cur.execute('INSERT INTO market_sector_classification(dataset_id,source_row_number,sector,ticker,company_name,raw_row_json,parse_status) VALUES (?,?,?,?,?,?,?)',(did,rownum,canonical(row,'Sector'),canonical(row,'Stock_code','Code','CODE'),canonical(row,'Stock_name','Name','NAME'),raw,'parsed'))
                    sector_count+=1; continue
                ticker=canonical(row,'Code','CODE'); company=canonical(row,'Name','NAME'); date_raw=canonical(row,'Date','DATE'); date=parse_date(date_raw)
                vals={
                  'low_12m':parse_num(canonical(row,'12m Low')),'high_12m':parse_num(canonical(row,'12m High')),
                  'day_low':parse_num(canonical(row,'Day Low')),'day_high':parse_num(canonical(row,'Day High')),
                  'day_price':parse_num(canonical(row,'Day Price')),'previous_price':parse_num(canonical(row,'Previous')),
                  'change_value':parse_num(canonical(row,'Change')),'change_percent':parse_num(canonical(row,'Change%')),
                  'volume':parse_num(canonical(row,'Volume')),'adjusted_price':parse_num(canonical(row,'Adjusted Price')),
                  'adjustment_factor':parse_num(canonical(row,'Adjust'))}
                flags=market_anomaly_flags(trading_date=date,ticker=ticker,day_price=vals['day_price'],day_low=vals['day_low'],day_high=vals['day_high'])
                status='review' if flags else 'not_reviewed'
                cur.execute('INSERT INTO market_observation(dataset_id,source_row_number,trading_date,ticker,company_name,low_12m,high_12m,day_low,day_high,day_price,previous_price,change_value,change_percent,volume,adjusted_price,adjustment_factor,raw_row_json,parse_status,anomaly_status,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(did,rownum,date,str(ticker).strip() if ticker else None,str(company).strip() if company else None,vals['low_12m'],vals['high_12m'],vals['day_low'],vals['day_high'],vals['day_price'],vals['previous_price'],vals['change_value'],vals['change_percent'],vals['volume'],vals['adjusted_price'],vals['adjustment_factor'],raw if flags else None,'parsed',status,'; '.join(flags) if flags else None))
                oid=cur.lastrowid; obs_count+=1
                for flag in flags:
                    cur.execute('INSERT INTO market_data_anomaly(dataset_id,observation_id,source_row_number,anomaly_type,severity,detail,detected_at,resolution_status) VALUES (?,?,?,?,?,?,?,?)',(did,oid,rownum,flag,'review',f'Original row retained; parser did not discard or impute the value: {flag}',now,'open')); anomaly_count+=1
        cur.execute('INSERT INTO market_import_file(dataset_id,original_archive,extracted_relative_path,file_sha256,byte_size,row_count,file_format,rights_status,notes) VALUES (?,?,?,?,?,?,?,?,?)',(did,archive,rel,sha,len(data),rows,'CSV',rights,'Every source row retained; duplicates across releases are intentionally preserved.'))
        manifest.append({'dataset_id':did,'filename':p.name,'source_path':rel,'archive':archive,'release_period':period,'rows':rows,'sha256':sha,'rights_status':rights,'source_url':url})
    con.commit(); con.close()
    (BASE/'data'/'market_data'/'market_data_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'datasets':dataset_count,'observations':obs_count,'sector_rows':sector_count,'anomalies':anomaly_count,'raw_files':len(manifest)},indent=2))
if __name__=='__main__': main()
