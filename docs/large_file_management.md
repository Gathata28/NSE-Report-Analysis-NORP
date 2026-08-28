# Large-File Management

The repository currently includes a SQLite database of approximately 70 MB. This is below GitHub’s 100 MB hard per-file limit but above the 50 MB recommendation. The database is retained in the default branch because it provides immediate offline access to the analysis-ready archive.

The repository also contains retrieved PDFs, source captures, and archive snapshots. **NORP will use GitHub Releases as the primary artifact-storage strategy for future versioned database snapshots and ZIP bundles.** This decision is made before expanding the collection engine so that new generated archives do not accumulate in the working tree or Git history.

| Strategy | NORP decision | Intended use | Trade-off |
| --- | --- | --- | --- |
| GitHub Releases | **Selected** | Versioned SQLite snapshots, ZIP bundles, and release manifests | Keeps the source tree lighter while preserving public downloadable releases |
| External object storage | Deferred | Consider only if release assets become too large or operational requirements change | Requires stable hosting, access policy, and checksum publication |
| Git LFS | Not selected | Not required for the current release-artifact plan | Requires LFS storage/bandwidth management and does not remove licensing review |
| Normal Git history | Limited | Source code, schemas, manifests, checksums, and compact examples | Unsuitable for repeated large binaries |

## Release-artifact requirements

Future full database snapshots and archive ZIP bundles must be attached to a tagged GitHub Release rather than committed as new historical copies. Each artifact release must include a machine-readable manifest containing:

- a stable GitHub Release asset URL;
- the SHA-256 checksum;
- a version or release label;
- artifact type and generation timestamp;
- source/database coverage summary; and
- applicable license metadata, including the CC BY 4.0 notice for licensed market data.

The default branch should retain code, schemas, documentation, compact examples, and the current compact database only while it remains within the repository size constraints. Any future migration of the current database must preserve its public download path through a release asset and update the repository documentation and citation guidance.

## Reproducible staging command

Use the release bundler from a checked-out repository and point it to a directory outside the project tree:

```bash
python scripts/bundle_outputs.py \
  --version 2026.08.28 \
  --output-dir /tmp/norp-release-2026.08.28
```

The command creates the versioned SQLite snapshot, an index ZIP bundle, a JSON release manifest, and a SHA-256 checksum file. The manifest contains the eventual GitHub Release asset URLs and license metadata. Upload the staged artifacts to the matching GitHub Release tag only after reviewing the manifest and checksums; the bundler does not publish releases automatically.
