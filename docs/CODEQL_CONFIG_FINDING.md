# CodeQL Configuration Finding

## Finding

GitHub CodeQL default setup and the committed advanced workflow were enabled at the same time. This caused GitHub to reject the advanced workflow’s SARIF uploads with the following error:

> CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled.

## Final decision

NORP uses **custom advanced CodeQL setup only**. GitHub default setup was disabled through the repository Code Scanning configuration, and `.github/workflows/codeql.yml` is the sole repository-managed CodeQL workflow.

The custom workflow analyzes:

- `python` source code;
- GitHub Actions workflow code (`actions`);
- the `security-extended` query suite; and
- pushes, pull requests targeting `main`, and a weekly scheduled run.

The workflow has explicit `security-events: write` permission so it can upload SARIF results. The separate `NORP checks` workflow remains responsible for compilation, unit tests, database integrity, market-data quality, and privacy-marker checks.

## Verification

The custom advanced CodeQL run for commit `312e368` completed successfully, including SARIF processing, and the NORP checks run for the same commit also completed successfully. The repository default-setup API reports `state: not-configured`.
