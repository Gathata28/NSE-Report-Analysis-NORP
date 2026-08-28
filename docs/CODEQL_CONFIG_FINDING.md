# CodeQL Configuration Finding

## Finding

GitHub CodeQL default setup is configured for the repository with `actions` and `python` languages. The remote `main` branch also contains `.github/workflows/codeql.yml`, an advanced CodeQL workflow. GitHub therefore rejects the advanced workflow's SARIF uploads with: `CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled`.

## Decision

Retain GitHub's configured default setup because it is already active and successfully analyzing both supported languages. Remove the duplicate committed advanced workflow so future pushes do not submit conflicting SARIF results.

## Verification evidence

- Default setup API state: `configured`
- Default setup languages: `actions`, `python`
- Remote workflows: `NORP checks`, `CodeQL Advanced`, `CodeQL` dynamic default setup
- Dynamic CodeQL analyses succeeded; advanced analyses failed only at SARIF processing due to the duplicate setup.
