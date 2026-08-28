# AfricanFinancials sitemap notes

## Source
- Requested URL: https://africanfinancials.com/wp-sitemap.xml
- Canonical URL returned: https://africanfinancials.com/sitemap_index.xml
- Page title: XML Sitemap
- Accessed: 2026-08-27

## Key finding
The XML sitemap index states that it contains 69 sitemaps and lists `document-sitemap.xml` through `document-sitemap35.xml`, with the newest partition modified 2026-08-26. This is a stronger enumeration path than the 310-page filtered HTML view because it is a machine-readable index of document post pages.

The document sitemap partitions cover historical intervals from 2018 through 2026, with older partitions showing modifications dating back to 2018 and newer partitions through 2026-08-26. The index also exposes `company-sitemap.xml`, which can help enumerate the repository's issuer directory.

## Research implication
Fetch and parse all document sitemap partitions. Then fetch each document page to extract its direct attached PDF or other downloadable report file, title, issuer, document type, report year, period, and source-page URL. Filter the resulting corpus to annual reports, interim/semi-annual reports, and quarter-specific reports, while retaining abridged annual/quarterly disclosures in a separate classification where they are the only public report form.
