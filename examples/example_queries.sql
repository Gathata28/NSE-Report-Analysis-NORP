-- Report catalog with preferred source and validation status
SELECT * FROM vw_report_catalog LIMIT 25;

-- Core annual, half-year, and quarterly records
SELECT issuer, ticker, report_frequency, report_year_label, document_title, source_tier
FROM vw_periodic_core_reports
ORDER BY issuer, report_year_label;

-- Facts requiring manual review
SELECT issuer, ticker, metric_name, value_text, source_page, quality_status
FROM vw_fact_panel
WHERE quality_status = 'needs_review'
LIMIT 100;
