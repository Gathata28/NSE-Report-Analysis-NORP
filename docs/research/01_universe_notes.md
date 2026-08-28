# NSE issuer-universe notes

## Primary source
- Webpage title: Listed Companies - Nairobi Securities Exchange PLC
- URL: https://www.nse.co.ke/listed-companies/
- Accessed: 2026-08-27 (user timezone)
- Page states current trading date: 27/08/2026.
- The page groups current issuers by sector and provides issuer name, trading symbol, and ISIN code. It includes some issuers that may be suspended, inactive, or not ordinary listed shares (for example ETFs and REITs); these are retained in the raw universe and will be classified in the final dataset.

## Current issuer names/tickers transcribed from the official page
Agricultural: Eaagads Ltd (EGAD); Kapchorua Tea Co. Ltd (KAPC); Kakuzi (KUKZ); Limuru Tea Co. Ltd (LIMT); Sasini Ltd (SASN); Williamson Tea Kenya Ltd (WTK).

Automobiles and accessories: Car and General (K) Ltd (CGEN).

Banking: Absa Bank Kenya PLC (ABSA); Stanbic Holdings Plc (SBIC); I&M Holdings Ltd (IMH); Diamond Trust Bank Kenya Ltd (DTK); Standard Chartered Bank Ltd (SCBK); Equity Group Holdings (EQTY); The Co-operative Bank of Kenya Ltd (COOP); BK Group PLC (BKG); Family Bank Limited (FMLY); HF Group Ltd (HFCK); KCB Group Ltd (KCB); NCBA Group PLC (NCBA).

Commercial and services: Express Ltd (XPRS); Sameer Africa PLC (SMER); Kenya Airways Ltd (KQ); Nation Media Group (NMG); Standard Group Ltd (SGL); TPS Eastern Africa (Serena) Ltd (TPSE); Scangroup Ltd (SCAN); Uchumi Supermarket Ltd (UCHM); Longhorn Publishers Ltd (LKL); Deacons (East Africa) Plc (DCON); Nairobi Business Ventures Ltd (NBV).

Construction and allied: Athi River Mining (ARM); Bamburi Cement PLC (BAMB); Crown Paints Kenya PLC (CRWN); E.A. Cables PLC (CABL); E.A. Portland Cement Ltd (PORT).

Energy and petroleum: Total Kenya Ltd (TOTL); KenGen Ltd (KEGN); Kenya Power & Lighting Co Ltd (KPLC); Umeme Ltd (UMME); Kenya Pipeline Company (KPC).

Insurance: Jubilee Holdings Ltd (JUB); Sanlam Allianz Holdings (Kenya) PLC (SLAM); Kenya Re-Insurance Corporation Ltd (KNRE); Liberty Kenya Holdings Ltd (LBTY); Britam Holdings Ltd (BRIT); CIC Insurance Group Ltd (CIC).

Investment: Olympia Capital Holdings Ltd (OCH); Centum Investment Co Ltd (CTUM); Trans-Century Ltd (TCL); Home Afrika Ltd (HAFR); Kurwitu Ventures (KURV).

Investment services: Nairobi Securities Exchange Ltd (NSE).

Manufacturing and allied: B.O.C Kenya Ltd (BOC); British American Tobacco Kenya Ltd (BAT); Carbacid Investments Ltd (CARB); East African Breweries Ltd (EABL); Mumias Sugar Co. Ltd (MSC); Unga Group Ltd (UNGA); Eveready East Africa Ltd (EVRD); Africa Mega Agricorp PLC (AMAC); Flame Tree Group Holdings Ltd (FTGH); Shri Krishana Overseas (SKL.O0000).

Telecommunication and technology: Safaricom PLC (SCOM).

Real estate investment trust: Laptrust Imara I-REIT (LAPR); ALP Industrial Real Estate Investment Trust (ALP); TRIFIC Green USD I-REIT (TRFC).

Exchange traded fund: New Gold Issuer (RP) Ltd (GLD); Satrix MSCI World Feeder ETF (SMWF.E0000).

## Caveats to resolve
- The page contains duplicate ticker tiles in its market ticker strip and issuer cards; deduplicate by ISIN/name.
- The current page is not a historical list. Historical and delisted issuers must be identified from NSE notices, issuer pages, CMA documents, official corporate histories, and reputable archival lists.
- The official page includes companies that may be suspended or inactive; status needs an explicit field rather than silently excluding them.
