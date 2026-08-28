# Large-File Management

The repository currently includes a SQLite database of approximately 70 MB. This is below GitHub’s 100 MB hard per-file limit but above the 50 MB recommendation. The database is retained in the default branch because it provides immediate offline access to the analysis-ready archive.

The repository also contains retrieved PDFs, source captures, and archive snapshots. Before adding more large binaries, maintainers should select one artifact policy:

| Strategy | Appropriate use | Trade-off |
| --- | --- | --- |
| GitHub Releases | Versioned database snapshots and ZIP bundles | Keeps the source tree lighter while preserving downloadable releases |
| External object storage | Large or frequently refreshed datasets | Requires stable hosting, access policy, and checksum publication |
| Git LFS | Large files that must remain versioned with Git | Requires LFS storage/bandwidth management and does not remove the need for licensing review |
| Normal Git history | Small source files and code | Simple, but unsuitable for repeated large binaries |

For future releases, keep code, schemas, manifests, checksums, and compact examples in normal Git history. Prefer release assets or external artifact storage for full database snapshots, duplicate PDFs, and ZIP bundles. Any moved artifact must retain a stable URL, SHA-256 checksum, release/version label, and license metadata in the repository manifest.
