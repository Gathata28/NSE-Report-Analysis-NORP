# Current NSE issuer coverage and gap disclosure

**Reference date:** 27 August 2026. The current universe is the 66-row official NSE issuer universe used in `current_nse_universe.csv`. “Represented” means at least one annual, semi-annual, quarterly, or periodic-results record is indexed; it does not mean complete year-by-year coverage or a fully downloaded corpus.

After the latest rebuild, **65 of 66 current NSE rows have at least one indexed record**. The following one remains without an indexed financial-report record:

| Ticker | Issuer | Current-page / official route | Status at reference date | Treatment |
|---|---|---|---|---|
| TRFC | TRIFIC Green USD I-REIT | `https://trific.co.ke/i-reit/` | Official page is a 2026 offering/listing page rather than an annual or periodic report archive | No prospectus indexed as a report; first reporting-period documents may not yet be publicly posted |

## Recently resolved special categories and fallback rows

**SMWF.E0000 / Satrix MSCI World Feeder ETF** is represented by nine issuer-controlled annual financial-statement media links for 2016 and 2017–2020 and 2022–2025. No 2021 entry was visible in the Satrix product-page archive and it remains an explicit year-level gap, not an invented placeholder.

**GLD / NewGold Issuer (RF) Limited** is represented by six annual financial-statement records from the official Absa Index and Structured Solutions public downloads API for 2022–2026 and 2020. The API archive did not yield a 2021 annual statement in this pass.

**LBTY / Liberty Kenya Holdings PLC** is represented by one CMA fallback annual-financial-statement reference for 2022. The issuer route remained Cloudflare-blocked and the link was slow during bounded retrieval; the record is clearly labeled `CMA/regulator fallback` and is not claimed as a completed local download.

**BKG / BK Group PLC** is represented by 56 official documents obtained from the issuer’s public document-center API. **NBV / Nairobi Business Ventures PLC** is represented by 22 official annual and six-month records. **LAPR / Laptrust Imara I-REIT** is represented by six official annual and semi-annual records.

## Additional fallback and status notes

ARM Cement, Mumias Sugar, E.A. Portland Cement, Uchumi, Trans-Century, Deacons, Eveready, Limuru Tea, and East African Cables now have individually indexed CMA/NSE fallback references where exact public documents were found. Several regulator links returned slow, partial, or HTML/error responses during bounded validation; those outcomes are retained in the validation sheet and must not be interpreted as functional-download confirmation.

A targeted CMA/NSE search for Kurwitu Ventures returned statistical bulletins and market-reference entries, but the official NSE announcements archive now supplies an exact 2020 annual financial-statements PDF. Statistical bulletins were not added as issuer reports because they contain market/reference data rather than issuer financial statements. AMAC is represented cautiously by predecessor-name Kenya Orchards reports because AMAC’s official site states it was formerly Kenya Orchards Ltd.; these are not relabeled AMAC-period documents.

## Important interpretation

The one row above is a **coverage gap, not a delisting conclusion**. A missing archive, current-page absence, suspended/under-administration descriptor, or inaccessible domain does not establish that an issuer was delisted. Status claims require an explicit NSE/CMA corporate-action, suspension, delisting, or issuer-status source.

For rows added through NSE/CMA, the workbook labels those records `NSE/exchange fallback` or `CMA/regulator fallback`. The current report corpus is not a claim that every public report has been downloaded: most records are source-page-linked, while only a bounded representative sample has HTTP evidence.
