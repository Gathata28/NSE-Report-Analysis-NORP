# Security Policy

## Reporting a vulnerability

Please do not disclose sensitive information in a public issue. Report suspected security vulnerabilities, credential exposure, unsafe network behavior, or malicious source-material concerns privately to the repository maintainer through the contact method listed in the repository profile.

Include the affected file, a concise reproduction, impact, and any proposed mitigation. Do not include private source archives, credentials, account information, or unpublished research materials in an issue or pull request.

## Scope

NORP is a source-archive and analysis tool. It does not provide investment advice, execute trades, or request credentials. Network collection scripts should use verified TLS, bounded timeouts, and public URLs only. Data-source licensing and attribution requirements are documented in `docs/market_data_licensing.md`.

## Responsible request pacing

Collection code must use the shared `fetch_with_retry()` helper in `scripts/norp_engine.py` rather than creating an unbounded global request pool. The helper applies a source-tier-specific retry policy and a semaphore per destination host. Issuer sites default to a small host cap, while NSE/CMA and secondary sources use stricter caps. Callers should reuse a session, avoid duplicate retrieval, preserve source-page provenance, and never disable TLS certificate verification. Any new scraper should be tested with archived fixtures before live retrieval is enabled.

## Automated security scanning

The repository uses immutable commit-SHA references for GitHub Actions. Bandit is configured as a gating scan and must exit nonzero when findings are detected. Semgrep runs as token-free Semgrep Community Edition against active Python code, tests, and workflow files, and uploads SARIF results to the repository Security tab; it does not rely on `SEMGREP_APP_TOKEN` or `SEMGREP_DEPLOYMENT_ID`. CodeQL uses the separate custom advanced workflow documented in `docs/CODEQL_CONFIG_FINDING.md`, with GitHub default setup disabled. OSV-Scanner checks declared dependencies and is expected to fail when vulnerable versions are declared.
