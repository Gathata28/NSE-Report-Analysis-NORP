# First-party issuer archive notes

## KCB Group
- Webpage title: Integrated Reports | KCB Bank
- URL: https://kcbgroup.com/integrated-reports
- Accessed: 2026-08-27
- The page identifies itself as an Investors Relations → Integrated Reports archive and exposes year filters 2016–2026. Visible entries include KCB Group Plc 2020, 2021, 2022, 2023, 2024, and 2025 Integrated Reports and Financial Statements.
- KCB also exposes separate first-party archive routes for Financial Statements and Investor Presentations from the same investor-relations navigation; these should be crawled separately for semi-annual and quarterly PDFs.
- The page is a direct issuer source. The underlying HTML should be parsed for the exact download hrefs, not reconstructed from titles.

## General source hierarchy now adopted
Issuer-hosted report/archive page and PDF first; official NSE financial-results/annual-report archive second; CMA or other statutory/regulatory source third; reputable public archive such as AfricanFinancials only as a discovery/fallback mirror. Each record will carry `source_tier` and `source_page_url` so the distinction is explicit.
