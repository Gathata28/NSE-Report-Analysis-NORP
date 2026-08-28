PRAGMA foreign_keys = ON;

CREATE TABLE issuer (
  issuer_id INTEGER PRIMARY KEY,
  canonical_name TEXT NOT NULL,
  canonical_ticker TEXT,
  sector TEXT,
  isin TEXT,
  listing_status TEXT,
  status_as_of TEXT,
  coverage_state TEXT NOT NULL DEFAULT 'unclassified',
  notes TEXT,
  UNIQUE(canonical_name, canonical_ticker)
);

CREATE TABLE issuer_alias (
  alias_id INTEGER PRIMARY KEY,
  issuer_id INTEGER NOT NULL REFERENCES issuer(issuer_id),
  alias_name TEXT NOT NULL,
  alias_ticker TEXT,
  alias_type TEXT NOT NULL,
  source_url TEXT,
  confidence TEXT NOT NULL DEFAULT 'unresolved',
  notes TEXT,
  UNIQUE(issuer_id, alias_name, alias_ticker)
);

CREATE TABLE listing_event (
  listing_event_id INTEGER PRIMARY KEY,
  issuer_id INTEGER NOT NULL REFERENCES issuer(issuer_id),
  event_type TEXT NOT NULL,
  event_date TEXT,
  event_text TEXT,
  source_url TEXT NOT NULL,
  source_tier TEXT NOT NULL,
  confidence TEXT NOT NULL DEFAULT 'unresolved',
  is_confirmed INTEGER NOT NULL DEFAULT 0 CHECK(is_confirmed IN (0,1)),
  notes TEXT
);

CREATE TABLE report (
  report_id TEXT PRIMARY KEY,
  issuer_id INTEGER NOT NULL REFERENCES issuer(issuer_id),
  ticker TEXT,
  report_frequency TEXT,
  document_subtype TEXT,
  core_report_flag INTEGER NOT NULL DEFAULT 0 CHECK(core_report_flag IN (0,1)),
  report_year_label TEXT,
  report_period_start TEXT,
  report_period_end TEXT,
  publication_date TEXT,
  document_title TEXT,
  webpage_title TEXT,
  collection_date TEXT,
  dedupe_group TEXT,
  notes TEXT
);

CREATE TABLE report_source (
  source_id INTEGER PRIMARY KEY,
  report_id TEXT NOT NULL REFERENCES report(report_id),
  source_page_url TEXT,
  download_url TEXT,
  source_tier TEXT NOT NULL,
  source_title TEXT,
  content_type TEXT,
  http_status INTEGER,
  final_url TEXT,
  publication_date TEXT,
  is_preferred INTEGER NOT NULL DEFAULT 0 CHECK(is_preferred IN (0,1)),
  UNIQUE(report_id, source_page_url, download_url)
);

CREATE TABLE report_validation (
  validation_id INTEGER PRIMARY KEY,
  report_id TEXT NOT NULL REFERENCES report(report_id),
  source_id INTEGER REFERENCES report_source(source_id),
  validation_date TEXT,
  validation_method TEXT,
  observed_content_type TEXT,
  http_status INTEGER,
  verification_status TEXT NOT NULL,
  error_text TEXT,
  evidence_text TEXT
);

CREATE TABLE report_file (
  file_id INTEGER PRIMARY KEY,
  report_id TEXT NOT NULL REFERENCES report(report_id),
  source_id INTEGER REFERENCES report_source(source_id),
  local_path TEXT NOT NULL,
  byte_size INTEGER,
  sha256 TEXT,
  retrieved_at TEXT,
  checksum_status TEXT NOT NULL DEFAULT 'not_checked',
  UNIQUE(report_id, local_path)
);

CREATE TABLE report_text (
  text_id INTEGER PRIMARY KEY,
  report_id TEXT NOT NULL REFERENCES report(report_id),
  file_id INTEGER REFERENCES report_file(file_id),
  page_number INTEGER,
  section_name TEXT,
  extraction_method TEXT NOT NULL,
  text_content TEXT NOT NULL,
  extraction_status TEXT NOT NULL DEFAULT 'extracted'
);

CREATE TABLE report_fact (
  fact_id INTEGER PRIMARY KEY,
  report_id TEXT NOT NULL REFERENCES report(report_id),
  file_id INTEGER REFERENCES report_file(file_id),
  metric_name TEXT NOT NULL,
  fact_type TEXT NOT NULL,
  value_numeric REAL,
  value_text TEXT,
  unit TEXT,
  currency TEXT,
  period_start TEXT,
  period_end TEXT,
  comparative_period_end TEXT,
  source_page INTEGER,
  source_locator TEXT,
  definition_text TEXT,
  quality_status TEXT NOT NULL DEFAULT 'needs_review',
  confidence TEXT NOT NULL DEFAULT 'unresolved',
  notes TEXT
);

CREATE TABLE report_qualitative (
  qualitative_id INTEGER PRIMARY KEY,
  report_id TEXT NOT NULL REFERENCES report(report_id),
  file_id INTEGER REFERENCES report_file(file_id),
  topic TEXT NOT NULL,
  statement_text TEXT NOT NULL,
  source_page INTEGER,
  source_locator TEXT,
  quality_status TEXT NOT NULL DEFAULT 'needs_review',
  confidence TEXT NOT NULL DEFAULT 'unresolved'
);

CREATE TABLE coverage_gap (
  gap_id INTEGER PRIMARY KEY,
  issuer_id INTEGER NOT NULL REFERENCES issuer(issuer_id),
  ticker TEXT,
  gap_scope TEXT NOT NULL,
  gap_description TEXT NOT NULL,
  reference_date TEXT NOT NULL,
  source_url TEXT,
  treatment TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open'
);

CREATE TABLE source_artifact (
  artifact_id INTEGER PRIMARY KEY,
  artifact_name TEXT NOT NULL UNIQUE,
  artifact_type TEXT NOT NULL,
  local_path TEXT NOT NULL,
  sha256 TEXT,
  source_url TEXT,
  description TEXT
);

CREATE TABLE extraction_run (
  run_id INTEGER PRIMARY KEY,
  run_started_at TEXT NOT NULL,
  run_completed_at TEXT,
  pipeline_version TEXT NOT NULL,
  input_record_count INTEGER,
  report_count INTEGER,
  issuer_count INTEGER,
  fact_count INTEGER,
  qualitative_count INTEGER,
  warning_count INTEGER,
  error_count INTEGER,
  notes TEXT
);

CREATE INDEX idx_report_issuer ON report(issuer_id);
CREATE INDEX idx_report_period ON report(report_period_end, report_year_label);
CREATE INDEX idx_report_source_tier ON report_source(source_tier);
CREATE INDEX idx_fact_metric_period ON report_fact(metric_name, period_end);
CREATE INDEX idx_gap_status ON coverage_gap(status, gap_scope);

CREATE VIEW vw_report_catalog AS
SELECT r.report_id, i.canonical_name AS issuer, COALESCE(r.ticker,i.canonical_ticker) AS ticker,
       r.report_frequency, r.document_subtype, r.core_report_flag, r.report_year_label,
       r.report_period_end, r.document_title, r.webpage_title, s.source_page_url,
       s.download_url, s.source_tier, v.verification_status, f.local_path, f.sha256
FROM report r JOIN issuer i ON i.issuer_id=r.issuer_id
LEFT JOIN report_source s ON s.report_id=r.report_id AND s.is_preferred=1
LEFT JOIN report_validation v ON v.validation_id=(SELECT MAX(v2.validation_id) FROM report_validation v2 WHERE v2.report_id=r.report_id)
LEFT JOIN report_file f ON f.file_id=(SELECT MAX(f2.file_id) FROM report_file f2 WHERE f2.report_id=r.report_id);

CREATE VIEW vw_periodic_core_reports AS
SELECT * FROM vw_report_catalog
WHERE core_report_flag=1 AND report_frequency IN ('Annual','Semi-annual','Quarterly','Periodic results material');

CREATE VIEW vw_fact_panel AS
SELECT f.*, r.ticker, i.canonical_name AS issuer
FROM report_fact f JOIN report r ON r.report_id=f.report_id JOIN issuer i ON i.issuer_id=r.issuer_id;

CREATE VIEW vw_data_quality_flags AS
SELECT r.report_id, i.canonical_name AS issuer, r.report_year_label, r.report_period_end,
       r.report_frequency, s.source_tier, v.verification_status,
       CASE WHEN r.report_period_end IS NULL THEN 'missing_period_end' END AS period_flag,
       CASE WHEN f.fact_id IS NOT NULL AND f.quality_status<>'validated' THEN 'fact_review_required' END AS fact_flag
FROM report r JOIN issuer i ON i.issuer_id=r.issuer_id
LEFT JOIN report_source s ON s.report_id=r.report_id AND s.is_preferred=1
LEFT JOIN report_validation v ON v.validation_id=(SELECT MAX(v2.validation_id) FROM report_validation v2 WHERE v2.report_id=r.report_id)
LEFT JOIN report_fact f ON f.report_id=r.report_id;
