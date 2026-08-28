# Pagination and corpus notes

## Verified page-2 source
- URL: https://africanfinancials.com/kenya-listed-company-documents/?wpv_view_count=21075&wpv_paged=2
- Same page title and filters as the base page.
- Page 2 returns 12 document records and exposes the same `/document/{slug}/` source-page pattern.
- The archive reports 310 pages in total, so a complete repository crawl should enumerate up to 3,720 result records before deduplication.
- Examples on page 2 include KenGen HY2026 Interim Report, Olympia Capital 2026 Annual Report and Abridged Report, Centum FY2026 Abridged Report, E.A. Portland Cement 2025 Annual Report, TPS Eastern Africa 2025 Annual Report, Sasini HY2026 Interim Report, Safaricom 2026 Annual Report, and Williamson Tea Kenya 2026 Annual Report.

## Access constraint
- Direct HTTP requests from the sandbox receive HTTP 403 from AfricanFinancials even with browser-like headers, while the authenticated browser session can access the pages. This means the repository may need browser-backed retrieval or another public endpoint rather than a plain requests crawler.
