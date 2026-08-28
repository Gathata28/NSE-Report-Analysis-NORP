from __future__ import annotations
# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv, hashlib, json, re, sqlite3, subprocess, shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__import__('os').environ.get('NORP_ROOT', Path(__file__).resolve().parents[1]))
ROOT = BASE / 'data' / 'indexes' if (BASE / 'data' / 'indexes' / 'nse_reports_normalized_validated.csv').exists() else BASE
PDF_ROOT = BASE / 'data' / 'retrieved' if (BASE / 'data' / 'retrieved').exists() else BASE
DB = ROOT / 'nse_reports_archive.sqlite'
SCHEMA = (BASE / 'schema' / 'nse_archive_schema.sql') if (BASE / 'schema' / 'nse_archive_schema.sql').exists() else ROOT / 'nse_archive_schema.sql'

def rows(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def val(row, *names):
    for n in names:
        x = row.get(n)
        if x not in (None, ''):
            return x.strip() if isinstance(x, str) else x
    return None

def nullable(x):
    return None if x in (None, '') else x

def norm_date(x):
    if not x:
        return None
    x = str(x).strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(x, fmt).date().isoformat()
        except ValueError:
            pass
    return x

def bool01(x):
    return 1 if str(x).lower() in ('1','yes','true','y') else 0

def source_tier(x):
    s = (x or '').lower()
    if 'secondary' in s or 'wikipedia' in s:
        return 'secondary_discovery_only'
    if 'cma' in s or 'regulator' in s:
        return 'cma_fallback'
    if 'nse' in s or 'exchange' in s:
        return 'nse_fallback'
    if 'api' in s or 'cdn' in s:
        return 'issuer_controlled_api_or_cdn'
    if 'issuer' in s or 'first' in s or 'official' in s:
        return 'issuer_first_party'
    return 'unknown'

def extract_pdf_pages(pdf_path):
    binary = shutil.which('pdftotext')
    if binary is None:
        raise RuntimeError('pdftotext is required to rebuild the database. Install poppler-utils and retry.')
    out = pdf_path.with_suffix('.txt')
    subprocess.run([binary,'-layout',str(pdf_path),str(out)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    text = out.read_text(errors='replace') if out.exists() else ''
    pages = [p.strip() for p in text.split('\f')]
    if any(len(p) >= 40 for p in pages):
        return [(i+1, p, 'pdftotext-layout') for i,p in enumerate(pages) if p]
    ocr = pdf_path.with_suffix('.ocr.txt')
    if ocr.exists():
        opages = [p.strip() for p in ocr.read_text(errors='replace').split('\f')]
        return [(i+1, p, 'tesseract-ocr') for i,p in enumerate(opages) if p]
    return [(i+1, p, 'pdftotext-layout') for i,p in enumerate(pages) if p]

def probable_facts(page_text):
    facts=[]
    for line in page_text.splitlines():
        line=' '.join(line.split())
        if not line or len(line)>240:
            continue
        m=re.match(r'^([A-Za-z][A-Za-z0-9 ,.&()/%\-]{2,100}?)\s+((?:\(?[0-9][0-9,\.]*\)?)(?:\s+[0-9][0-9,\.]*\)?){0,3})$',line)
        if m:
            nums=re.findall(r'\(?[0-9][0-9,\.]*\)?',m.group(2))
            facts.append((m.group(1).strip(), line, nums))
    return facts

def main():
    master=rows(ROOT/'nse_reports_normalized_validated.csv')
    current=rows(ROOT/'current_nse_universe.csv')
    hist=rows(ROOT/'historical_nse_universe.csv')
    gaps=rows(ROOT/'current_gap_disclosures.csv')
    validation=rows(ROOT/'nse_link_validation_sample.csv')
    manifest=rows(ROOT/'downloaded_files_manifest.csv')
    if DB.exists(): DB.unlink()
    con=sqlite3.connect(DB)
    con.executescript(SCHEMA.read_text())
    cur=con.cursor()
    now=datetime.now(timezone.utc).isoformat()
    cur.execute('INSERT INTO extraction_run(run_started_at,pipeline_version,input_record_count,notes) VALUES (?,?,?,?)',(now,'nse-relational-v1',len(master),'Metadata imported from normalized archive; local PDF text/fact extraction is conservative and review-flagged.'))
    run_id=cur.lastrowid

    issuer_keys={}
    issuer_rows=list(current)+list(hist)
    for r in issuer_rows:
        ticker=val(r,'ticker','Ticker')
        name=val(r,'legal_or_display_name','issuer','Issuer') or 'Unknown issuer'
        key=(ticker or '', name.lower())
        if key in issuer_keys: continue
        cur.execute('INSERT INTO issuer(canonical_name,canonical_ticker,sector,isin,listing_status,status_as_of,coverage_state,notes) VALUES (?,?,?,?,?,?,?,?)',(
            name,ticker,nullable(val(r,'sector')),nullable(val(r,'isin')),nullable(val(r,'status_as_of_2026-08-27','listing_status')), '2026-08-27', 'historical_candidate' if 'historical' in (val(r,'status_as_of_2026-08-27') or '').lower() or 'absent' in (val(r,'status_as_of_2026-08-27') or '').lower() else 'current_or_candidate', nullable(val(r,'notes'))))
        issuer_keys[key]=cur.lastrowid
    for r in master:
        ticker=val(r,'ticker'); name=val(r,'issuer') or 'Unknown issuer'; key=(ticker or '',name.lower())
        if key not in issuer_keys:
            cur.execute('INSERT INTO issuer(canonical_name,canonical_ticker,coverage_state) VALUES (?,?,?)',(name,ticker,'report_only'))
            issuer_keys[key]=cur.lastrowid
    for r in hist:
        ticker=val(r,'ticker'); name=val(r,'legal_or_display_name') or 'Unknown issuer'; iid=issuer_keys.get((ticker or '',name.lower()))
        if iid and val(r,'notes') and 'predecessor' in val(r,'notes').lower():
            cur.execute('INSERT OR IGNORE INTO issuer_alias(issuer_id,alias_name,alias_ticker,alias_type,source_url,confidence,notes) VALUES (?,?,?,?,?,?,?)',(iid,'Kenya Orchards Limited','ORCH','predecessor_name',val(r,'status_source_url'),'medium',val(r,'notes')))
    for r in master:
        rid=val(r,'record_id'); ticker=val(r,'ticker'); name=val(r,'issuer') or 'Unknown issuer'; iid=issuer_keys[(ticker or '',name.lower())]
        cur.execute('INSERT INTO report VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
            rid,iid,ticker,nullable(val(r,'report_frequency')),nullable(val(r,'document_subtype')),bool01(val(r,'core_report_flag')),nullable(val(r,'report_year_label')),None,norm_date(val(r,'report_period_end')),norm_date(val(r,'publication_date')),nullable(val(r,'document_title')),nullable(val(r,'webpage_title')),nullable(val(r,'collection_date')),nullable(val(r,'dedupe_group')),nullable(val(r,'notes'))))
        st=source_tier(val(r,'source_tier'))
        cur.execute('INSERT INTO report_source(report_id,source_page_url,download_url,source_tier,source_title,content_type,http_status,final_url,publication_date,is_preferred) VALUES (?,?,?,?,?,?,?,?,?,1)',(rid,nullable(val(r,'source_page_url')),nullable(val(r,'download_url')),st,nullable(val(r,'document_title') or val(r,'webpage_title')),nullable(val(r,'content_type')),int(val(r,'http_status')) if str(val(r,'http_status') or '').isdigit() else None,nullable(val(r,'final_url')),norm_date(val(r,'publication_date'))))
        sid=cur.lastrowid
        status=val(r,'link_verification_status') or ('sample_validated' if val(r,'http_status') in ('200','206') else 'issuer_link_pending')
        cur.execute('INSERT INTO report_validation(report_id,source_id,validation_date,validation_method,observed_content_type,http_status,verification_status,error_text,evidence_text) VALUES (?,?,?,?,?,?,?,?,?)',(rid,sid,norm_date(val(r,'validation_date')),nullable(val(r,'validation_method')),nullable(val(r,'content_type_observed') or val(r,'content_type')),int(val(r,'http_status')) if str(val(r,'http_status') or '').isdigit() else None,status,nullable(val(r,'validation_error')),None))
    def resolve_issuer(ticker, name):
        key=(ticker or '', (name or '').lower())
        if key in issuer_keys: return issuer_keys[key]
        matches=[iid for (t,n),iid in issuer_keys.items() if ticker and t==ticker]
        return matches[0] if matches else None
    for r in gaps:
        ticker=val(r,'ticker'); name=val(r,'issuer') or 'Unknown issuer'; iid=resolve_issuer(ticker,name)
        if iid:
            cur.execute('INSERT INTO coverage_gap(issuer_id,ticker,gap_scope,gap_description,reference_date,source_url,treatment,status) VALUES (?,?,?,?,?,?,?,?)',(iid,ticker,'current_universe',val(r,'status_at_reference_date') or '', '2026-08-27',val(r,'official_route'),val(r,'treatment') or '', 'open'))
    for r in manifest:
        rid=val(r,'record_id','report_id')
        path=val(r,'local_path','path','file_path')
        if not rid or not path: continue
        p=PDF_ROOT/path if not str(path).startswith('/') else Path(path)
        if not p.exists(): continue
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        cur.execute('SELECT source_id FROM report_source WHERE report_id=? ORDER BY source_id LIMIT 1',(rid,)); s=cur.fetchone()
        cur.execute('INSERT OR IGNORE INTO report_file(report_id,source_id,local_path,byte_size,sha256,retrieved_at,checksum_status) VALUES (?,?,?,?,?,?,?)',(rid,s[0] if s else None,str(p.relative_to(BASE) if p.is_relative_to(BASE) else p),p.stat().st_size,sha,now,'verified'))
        cur.execute('SELECT file_id FROM report_file WHERE report_id=? AND local_path=?',(rid,str(p.relative_to(BASE) if p.is_relative_to(BASE) else p))); file_id=cur.fetchone()[0]
        for page_no,text,method in extract_pdf_pages(p):
            cur.execute('INSERT INTO report_text(report_id,file_id,page_number,section_name,extraction_method,text_content,extraction_status) VALUES (?,?,?,?,?,?,?)',(rid,file_id,page_no,None,method,text,'extracted'))
            cur.execute('INSERT INTO report_qualitative(report_id,file_id,topic,statement_text,source_page,source_locator,quality_status,confidence) VALUES (?,?,?,?,?,?,?,?)',(rid,file_id,'unclassified_ocr_text',text,page_no,'complete OCR page text','needs_review','unresolved'))
            for metric,line,nums in probable_facts(text):
                cur.execute('INSERT INTO report_fact(report_id,file_id,metric_name,fact_type,value_numeric,value_text,unit,currency,period_start,period_end,comparative_period_end,source_page,source_locator,definition_text,quality_status,confidence,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(rid,file_id,metric,'candidate_numeric',None,line,None,None,None,None,None,page_no,'line-level heuristic',None,'needs_review','unresolved','Automatically surfaced from local PDF text; numeric parsing intentionally withheld until manual/table validation.'))
    for r in validation:
        rid=val(r,'record_id','report_id')
        if rid:
            cur.execute('UPDATE report_validation SET validation_date=COALESCE(validation_date,?),validation_method=COALESCE(validation_method,?),observed_content_type=COALESCE(observed_content_type,?),http_status=COALESCE(http_status,?),verification_status=?,error_text=COALESCE(error_text,?) WHERE report_id=?',(norm_date(val(r,'validation_date')),val(r,'validation_method'),val(r,'content_type_observed','content_type'),int(val(r,'http_status')) if str(val(r,'http_status') or '').isdigit() else None,val(r,'verification_status') or val(r,'status') or 'sample_validated',val(r,'error','validation_error'),rid))
    artifacts=['nse_reports_normalized_validated.csv','nse_first_party_tranche_index.csv','current_nse_universe.csv','current_issuer_coverage_log.csv','historical_nse_universe.csv','current_gap_disclosures.csv','nse_link_validation_sample.csv','downloaded_files_manifest.csv']
    for name in artifacts:
        p=ROOT/name
        if p.exists(): cur.execute('INSERT INTO source_artifact(artifact_name,artifact_type,local_path,sha256,description) VALUES (?,?,?,?,?)',(name,'csv',str(p.relative_to(BASE) if p.is_relative_to(BASE) else p),hashlib.sha256(p.read_bytes()).hexdigest(), 'Imported or supporting archive artifact'))
    cur.execute('UPDATE extraction_run SET run_completed_at=?,report_count=?,issuer_count=?,fact_count=(SELECT COUNT(*) FROM report_fact),qualitative_count=(SELECT COUNT(*) FROM report_qualitative),warning_count=(SELECT COUNT(*) FROM report_fact WHERE quality_status<>"validated"),error_count=0 WHERE run_id=?',(datetime.now(timezone.utc).isoformat(),len(master),len(issuer_keys),run_id))
    con.commit()
    print(json.dumps({'database':str(DB),'reports':len(master),'issuers':len(issuer_keys),'facts':cur.execute('SELECT COUNT(*) FROM report_fact').fetchone()[0],'text_rows':cur.execute('SELECT COUNT(*) FROM report_text').fetchone()[0],'files':cur.execute('SELECT COUNT(*) FROM report_file').fetchone()[0],'gaps':cur.execute('SELECT COUNT(*) FROM coverage_gap').fetchone()[0]},indent=2))
    con.close()
if __name__=='__main__': main()
