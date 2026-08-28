# Security Policy

## Reporting a vulnerability

Please do not disclose sensitive information in a public issue. Report suspected security vulnerabilities, credential exposure, unsafe network behavior, or malicious source-material concerns privately to the repository maintainer through the contact method listed in the repository profile.

Include the affected file, a concise reproduction, impact, and any proposed mitigation. Do not include private source archives, credentials, account information, or unpublished research materials in an issue or pull request.

## Scope

NORP is a source-archive and analysis tool. It does not provide investment advice, execute trades, or request credentials. Network collection scripts should use verified TLS, bounded timeouts, and public URLs only. Data-source licensing and attribution requirements are documented in `docs/market_data_licensing.md`.

## Responsible request pacing

Collection code must use the shared `fetch_with_retry()` helper in `scripts/norp_engine.py` rather than creating an unbounded global request pool. The helper applies a source-tier-specific retry policy and a semaphore per destination host. Issuer sites default to a small host cap, while NSE/CMA and secondary sources use stricter caps. Callers should reuse a session, avoid duplicate retrieval, preserve source-page provenance, and never disable TLS certificate verification. Any new scraper should be tested with archived fixtures before live retrieval is enabled.
