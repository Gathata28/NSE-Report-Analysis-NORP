# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,json,re,os,urllib.parse
from pathlib import Path
root=Path(str(PROJECT_ROOT))
rows=[];seen=set()
def clean(x):return re.sub(r'\s+',' ',' '.join(str(x or '').split())).strip()
def year(title,url=''):
 vals=re.findall(r'20\d{2}',title+' '+url)
 return vals[0] if vals else ''
def classify(title):
 low=title.lower(); y=year(title)
 if any(k in low for k in ['half year','half-year','h1','hy ','interim','six months','30 june','30th june']):freq='Semi-annual / half-year'
 elif re.search(r'\bq[1-4]\b|quarter|31 march|31st march|30 september|30th september|q[1-4]',low):freq='Quarterly'
 elif any(k in low for k in ['annual report','integrated report','full year','full-year','fy ','audited results','audited financial']):freq='Annual / full-year'
 else:freq='Periodic results material'
 if any(k in low for k in ['presentation','briefing','investor brief']):sub='Investor presentation'
 elif any(k in low for k in ['booklet','abridged','infograph']):sub='Results booklet / abridged report'
 elif any(k in low for k in ['press release','press-release','press commentary','commentary','announcement']):sub='Results announcement / commentary'
 elif any(k in low for k in ['annual report','integrated report']):sub='Annual report'
 elif any(k in low for k in ['financial statement','financial statements','financials','financial results','results']):sub='Financial results / statements'
 else:sub='Periodic results material'
 return y,freq,sub
def add(issuer,ticker,page_title,page_url,title,url,tier='Issuer website',pub=''):
 title=clean(title);url=clean(url)
 if not url or not title or url.startswith('#'):return
 low=title.lower()
 if any(k in low for k in ['agm','proxy','governance','policy','sustainability','board charter','risk committee','unit trust','tariff']):return
 if (issuer,url) in seen:return
 y,freq,sub=classify(title)
 rows.append({'record_id':'','issuer':issuer,'ticker':ticker,'report_frequency':freq,'document_subtype':sub,'report_year_label':y,'webpage_title':clean(page_title) or title,'source_page_url':page_url,'download_url':url,'http_status':'linked from issuer page','content_type':'application/pdf (inferred from source link)','source_tier':tier,'publication_date':pub});seen.add((issuer,url))
def read_csv(path):return list(csv.DictReader(open(root/path,encoding='utf-8')))
def add_simple(path,issuer,ticker,page_title,page_url,title_col='title',url_col='url',tier='Issuer website'):
 for r in read_csv(path):add(issuer,ticker,page_title,page_url,r.get(title_col,''),r.get(url_col,''),tier,r.get('publication_date',''))
# Original tranche: Safaricom.
add_simple('safaricom_annual_links.csv','Safaricom PLC','SCOM','Safaricom — Annual Reports','https://www.safaricom.co.ke/investor-relations-landing/reports/annual-reports','link_text','direct_url')
add_simple('safaricom_results_links.csv','Safaricom PLC','SCOM','Safaricom Financial Reports','https://www.safaricom.co.ke/investor-relations-landing/reports/financial-report/financial-results','link_text','direct_url')
# Equity and KCB links captured in the shared issuer archive sample.
for r in read_csv('issuer_archive_links_sample.csv'):
 ctx=r.get('issuer_context',''); title=r.get('link_text',''); low=title.lower()
 if ctx=='Equity Group' and not re.search(r'board|committee|charter|governance|risk|policy|tor',low):add('Equity Group Holdings PLC','EQTY','Equity Group — Investor Relations',r.get('archive_page_url','https://equitygroupholdings.com/investor-relations/'),title,r.get('direct_url',''))
 elif ctx=='KCB Group' and ('integrated report' in low or 'financial' in low or 'results' in low):add('KCB Group PLC','KCB','KCB Group — Investor Relations',r.get('archive_page_url','https://kcbgroup.com/financial-statements'),title,r.get('direct_url',''))
for r in json.load(open(root/'kcb_financial_links_full.json',encoding='utf-8')):add('KCB Group PLC','KCB','KCB Group — Financial Statements','https://kcbgroup.com/financial-statements',r.get('text',''),r.get('href',''))
add_simple('coop_integrated_links.csv','Co-operative Bank of Kenya PLC','COOP','Co-operative Bank — Integrated Reports','https://www.co-opbank.co.ke/investor-relations/integrated-reports/','link_text','direct_url')
add_simple('coop_financial_links.csv','Co-operative Bank of Kenya PLC','COOP','Co-operative Bank — Financial Statements','https://www.co-opbank.co.ke/investor-relations/financial-statements/','link_text','direct_url')
# Original issuer-level sources.
configs=[('eabl_financial_results_links.csv','East African Breweries PLC','EABL','EABL — Financial Results','https://www.eabl.com/investors/financial-results'),('ncba_quarterly_links.csv','NCBA Group PLC','NCBA','NCBA — Quarterly Earnings','https://ncbagroup.com/quarterly-earnings'),('im_report_links.csv','I&M Group PLC','IMH','I&M — Financial Results, Annual Reports and Investor Presentations','https://www.imbankgroup.com/financial-results-annual-reports-and-investor-presentation/'),('scb_report_links.csv','Standard Chartered Bank Kenya PLC','SCBK','Standard Chartered Kenya — Investor Relations','https://www.sc.com/ke/investor-relations/'),('kplc_report_links.csv','Kenya Power and Lighting PLC','KPLC','Kenya Power — Annual Reports','https://www.kplc.co.ke/annual-reports'),('kengen_report_links.csv','KenGen PLC','KEGN','KenGen — Financial Information','https://www.kengen.co.ke/investor-relations/financial-information/'),('absa_report_links.csv','Absa Bank Kenya PLC','ABSA','Absa — Investor Relations','https://www.absabank.co.ke/investor-relations/'),('stanbic_report_links.csv','Stanbic Holdings PLC','SBIC','Stanbic Holdings — Investor Relations','https://www.stanbicbank.co.ke/kenya/personal/about-us/investor-relations'),('dtb_quarterly_links.csv','Diamond Trust Bank Kenya PLC','DTK','DTB — Quarterly Financial Reports','https://dtbk.dtbafrica.com/quarterly-financial-reports'),('jubilee_annual_links.csv','Jubilee Holdings PLC','JUB','Jubilee — Annual Reports','https://jubileeinsurance.com/group/investor-relations/annual-reports/'),('britam_annual_links.csv','Britam Holdings PLC','BRIT','Britam — Annual Reports','https://www.britam.com/investor-relations/annual-reports')]
for path,issuer,ticker,pt,pu in configs:
 if not (root/path).exists():continue
 if path=='ncba_quarterly_links.csv':
  for r in read_csv(path):add(issuer,ticker,pt,r.get('source_page_url',pu),r.get('title',''),r.get('direct_url',''),pub=r.get('publication_date',''))
 elif path=='kengen_report_links.csv':
  for r in read_csv(path):add(issuer,ticker,pt,r.get('page_url',pu),r.get('title',''),r.get('download_url',''))
 elif path=='britam_annual_links.csv':
  for r in read_csv(path):add(issuer,ticker,pt,pu,r.get('title',''),r.get('url',''))
 else:add_simple(path,issuer,ticker,pt,pu)
# Later first-party additions.
add_simple('cic_report_links.csv','CIC Insurance Group PLC','CIC','CIC — Investor Relations','https://www.cicinsurancegroup.com/investor-relations/')
add_simple('unga_report_links.csv','Unga Group PLC','UNGA','Unga Group — Annual Reports and Financial Statements','https://unga-group.com/download-category/annual-reports-and-financial-statements/','title','url')
add_simple('crown_report_links.csv','Crown Paints Kenya PLC','CRWN','Crown Paints — Reports','https://www.crownpaints.co.ke/annual-reports-test/','title','url')
add_simple('kq_annual_report_links.csv','Kenya Airways PLC','KQ','Kenya Airways — Annual Reports','https://corporate.kenya-airways.com/en/investors-shareholders/annual-reports/','title','url')
add_simple('kq_financial_report_links.csv','Kenya Airways PLC','KQ','Kenya Airways — Financial Results','https://corporate.kenya-airways.com/en/investors-shareholders/financial-results/','title','url')
add_simple('bat_report_links.csv','British American Tobacco Kenya PLC','BAT','BAT Kenya — Financial and Sustainability Reports','https://www.batkenya.com/investors-and-reporting/financial-sustainability-reports','title','url')
add_simple('centum_annual_report_links.csv','Centum Investment Company PLC','CTUM','Centum — Annual Reports','https://centum.co.ke/annual-reports/','title','url')
add_simple('centum_financial_report_links.csv','Centum Investment Company PLC','CTUM','Centum — Financial Results','https://centum.co.ke/financial-results/','title','url')
add_simple('kenyare_annual_report_links.csv','Kenya Reinsurance Corporation PLC','KNRE','Kenya Re — Annual Reports','https://www.kenyare.co.ke/investor-relations/agm/annual-reports','title','url')
add_simple('kenyare_financial_report_links.csv','Kenya Reinsurance Corporation PLC','KNRE','Kenya Re — Financial Reports','https://www.kenyare.co.ke/investor-relations/financial-reports','title','url')
add_simple('kakuzi_report_links.csv','Kakuzi PLC','KUKZ','Kakuzi — Company Reports','https://www.kakuzi.co.ke/company-reports','title','url')
for r in read_csv('sasini_report_links.csv'):add('Sasini PLC','SASN','Sasini — Downloads','https://sasini.co.ke/downloads/',r.get('title',''),r.get('url',''))
for r in read_csv('carbacid_report_links.csv'):add('Carbacid Investments PLC','CARB','Carbacid — Official Site',r.get('source_page_url','https://carbacid.com/'),r.get('title',''),r.get('url',''))
add_simple('total_report_links.csv','TotalEnergies Marketing Kenya PLC','TOTL','TotalEnergies Marketing Kenya — Financials','https://totalenergies.ke/about-us/shareholder-information/financials')
add_simple('longhorn_report_links.csv','Longhorn Publishers PLC','LKL','Longhorn Publishers — Reports','https://www.longhornpublishers.com/investor-relations/reports/')
add_simple('flametree_report_links.csv','Flame Tree Group Holdings PLC','FTGH','Flame Tree Group — Financial Reports','https://flametreegroup.com/financial-reports')
add_simple('boc_report_links.csv','BOC Kenya PLC','BOC','BOC Kenya — Investor Relations','https://www.boc.co.ke/our-business/investor-relations')
add_simple('nse_issuer_annual_links.csv','Nairobi Securities Exchange PLC','NSE','NSE PLC — Annual Reports','https://www.nse.co.ke/annual-reports/')
add_simple('nmg_report_links.csv','Nation Media Group PLC','NMG','Nation Media Group — Financial Reports','https://www.nationmedia.com/investor-relations/financial-reports/')
add_simple('jubilee_report_links.csv','Jubilee Holdings PLC','JUB','Jubilee — Annual Reports','https://jubileeinsurance.com/group/investor-relations/annual-reports/')
add('Nation Media Group PLC','NMG','NMG HY2026 Results - The Nation Media Group','https://www.nationmedia.com/investor_news/nmg-hy2026-results/','NMG HY2026 Results','https://www.nationmedia.com/wp-content/uploads/2026/08/H1-2026-Results.pdf','Issuer website','2026-08-20')
add_simple('cargen_report_links.csv','Car & General (Kenya) PLC','CGEN','Car & General — Financial Reports','https://cargen.com/financial-reports/')
add_simple('sgl_report_links.csv','Standard Group PLC','SGL','Standard Group — Investors','https://www.standardmedia.co.ke/corporate/investors')
add_simple('scangroup_report_links.csv','WPP-Scangroup PLC','SCAN','WPP-Scangroup — Investor Relations','https://wpp-scangroup.com/investor-relations/')
add_simple('olympia_report_links.csv','Olympia Capital Holdings PLC','OCH','Olympia Capital — Reports','https://ochl.co.ke/investment/')
add_simple('sameer_report_links.csv','Sameer Africa PLC','SMER','Sameer Africa — Financial Reports','https://sameerafrica.com/financial-reports/')
add_simple('eaagads_report_links.csv','Eaagads PLC','EGAD','Eaagads — Annual Reports and Financial Statements','https://www.eaagads.co.ke/annual-reports-and-financial-statements/')
for r in read_csv('home_afrika_report_links.csv'):
 add('Home Afrika PLC','HAFR','Home Afrika — Annual Reports','https://www.homeafrika.com/investor-info/annual-reports',r.get('title',''),r.get('url',''),pub=r.get('report_date',''))
add_simple('express_report_links.csv','Express Kenya PLC','XPRS','Express Kenya — Investor Relations','https://expresskenya.co.ke/investor-relations/')
add_simple('umeme_report_links.csv','Umeme PLC','UMME','Umeme — Annual Reports and Financial Publications','https://www.umeme.co.ug/investor-relations/reports/136')
add_simple('sanlam_allianz_report_links.csv','Sanlam Allianz Holdings Kenya PLC','SLAM','Sanlam Allianz Kenya — Investor Relations','https://ke.sanlamallianz.com/life-insurance/about/our-profile#investor-relations')
for r in read_csv('bamburi_report_links_resolved.csv'):add('Bamburi Cement PLC','BAMB',r.get('title',''),'https://bamburigroup.com/bamburi-cement-investor-relations/annual-reports/',r.get('title',''),r.get('url',''))
add_simple('bamburi_h1_report_links.csv','Bamburi Cement PLC','BAMB','Bamburi Cement — H1 Financial Statements','https://bamburigroup.com/bamburi-unaudited-half-year-group-financial-statements-fy-2025/')
add_simple('tpse_serena_report_links.csv','TPS Eastern Africa PLC','TPSE','TPS Eastern Africa / Serena Hotels — Annual and Financial Reports','https://www.serenahotels.com/about-us/governance',tier='Issuer-controlled CDN linked from issuer page')
for r in read_csv('limuru_nse_fallback_links.csv'):add('Limuru Tea PLC','LIMT','Limuru Tea — NSE listed-company announcement','https://www.nse.co.ke/listed-company-announcements/',r.get('title',''),r.get('url',''),'NSE/exchange fallback')
for r in read_csv('eveready_cma_report_links.csv'):add('Eveready East Africa PLC','EVRD','Eveready East Africa — CMA fallback archive','https://www.cmarcp.or.ke/',r.get('title',''),r.get('url',''),'CMA/regulator fallback')
for r in read_csv('laptrust_report_links.csv'):add('Laptrust Imara I-REIT','LAPR','Laptrust Imara I-REIT — official investor reports',r.get('source_page',''),r.get('title',''),r.get('url',''),'Issuer website')
for r in read_csv('cma_construction_manufacturing_report_links.csv'):add(r.get('issuer',''),r.get('ticker',''),'CMA fallback archive — construction and manufacturing',r.get('source_page',''),r.get('title',''),r.get('url',''),'CMA/regulator fallback')
for r in read_csv('deacons_cma_report_links.csv'):add('Deacons (East Africa) PLC','DCON','Deacons — CMA fallback archive','https://annualreport.cma.or.ke/',r.get('title',''),r.get('url',''),'CMA/regulator fallback')
for r in read_csv('cma_uchumi_tcl_report_links.csv'):add(r.get('issuer',''),r.get('ticker',''),'CMA fallback archive — Uchumi and Trans-Century',r.get('source_page',''),r.get('title',''),r.get('url',''),'CMA/regulator fallback')
add_simple('nbv_report_links.csv','Nairobi Business Ventures PLC','NBV','Nairobi Business Ventures — Annual and Financial Reports','https://www.nbvplc.com/annual.html')
add_simple('bk_group_report_links.csv','BK Group PLC','BKG','BK Group — official financial reports API archive','https://bk.rw/en/about/document-center')
add_simple('satrix_msci_world_report_links.csv','Satrix MSCI World Feeder ETF','SMWF.E0000','Satrix MSCI World — Annual Financial Statements','https://satrix.co.za/products/product-details?id=33')
add_simple('newgold_report_links.csv','NewGold Issuer (RF) Limited','GLD','NewGold ETF — Annual Financial Statements','https://aiss.absa.africa/product/etf/ZAE000060067/GHA/downloads')
add_simple('liberty_cma_report_links.csv','Liberty Kenya Holdings PLC','LBTY','Liberty Kenya — CMA fallback annual statements','https://annualreport.cma.or.ke/')
for r in read_csv('kenya_orchards_report_links.csv'):add('Kenya Orchards Limited','ORCH','Kenya Orchards — CMA fallback annual reports',r.get('source_page','https://annualreport.cma.or.ke/'),r.get('title',''),r.get('url',''),'CMA/regulator fallback')
for r in read_csv('homeboyz_report_links.csv'):add('Homeboyz Entertainment PLC','HBE','Homeboyz Entertainment — Investor Center',r.get('source_page','https://homeboyz.co.ke/investor-relations'),r.get('title',''),r.get('url',''),'Issuer website')
for r in read_csv('skl_nse_report_links.csv'):add('Shri Krishana Overseas PLC','SKL.O0000','NSE listed-company announcements',r.get('source_page','https://www.nse.co.ke/listed-company-announcements/'),r.get('title',''),r.get('url',''),'NSE/exchange fallback')
for r in read_csv('cabl_nse_report_links.csv'):add('East African Cables PLC','CABL','NSE listed-company announcements',r.get('source_page','https://www.nse.co.ke/listed-company-announcements/'),r.get('title',''),r.get('url',''),'NSE/exchange fallback')
for r in read_csv('kurv_nse_report_links.csv'):add('Kurwitu Ventures Ltd','KURV','NSE listed-company announcements',r.get('source_page','https://www.nse.co.ke/listed-company-announcements/'),r.get('title',''),r.get('url',''),'NSE/exchange fallback')
for r in read_csv('amac_predecessor_report_links.csv'):add('Africa Mega Agricorp PLC','AMAC','AMAC predecessor-name report archive',r.get('source_page','https://amacplc.com/'),r.get('title',''),r.get('url',''),'CMA/regulator fallback; predecessor-name report')
for r in read_csv('williamson_report_links.csv'):
 add(r.get('issuer',''),r.get('ticker',''), 'Williamson Tea — Investor Reports','https://www.williamsontea.com/investor-reports/',r.get('title',''),r.get('url',''))
add_simple('family_annual_report_links.csv','Family Bank Limited','FMLY','Family Bank — Annual Reports','https://familybank.co.ke/?page_id=1773')
for r in read_csv('family_financial_report_links.csv'):add('Family Bank Limited','FMLY','Family Bank — Financial Results','https://familybank.co.ke/?page_id=654',r.get('title',''),r.get('url',''),pub=r.get('publication_date',''))
for r in read_csv('nbk_report_links.csv'):add('National Bank of Kenya PLC','NBK','National Bank — Investor Relations','https://www.nationalbank.co.ke/investor-relations',r.get('title',''),r.get('url',''),'Historical issuer website')
for r in read_csv('hfcb_report_links.csv'):add('HF Group PLC','HFCK','HFCB — Investor Relations','https://hfcb.co.ke/investor-relations',r.get('title',''),r.get('url',''),'Historical/current successor issuer website')
# Write only after complete assembly; stable identifiers are assigned here.
for i,r in enumerate(rows,1):r['record_id']=f'NSE-{i:05d}'
fields=['record_id','issuer','ticker','report_frequency','document_subtype','report_year_label','webpage_title','source_page_url','download_url','http_status','content_type','source_tier','publication_date']
with open(root/'nse_first_party_tranche_index.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
from collections import Counter
print('records',len(rows),'issuers',len(set(r['issuer'] for r in rows)))
print(Counter(r['issuer'] for r in rows))
