# Infra resources — 2026-10-17

| Category | Archive files | Package | Compressed size |
| --- | ---: | --- | ---: |
| `corpus` | 1 | [corpus-ab5947391ce6.tar.gz](dist/corpus-ab5947391ce6.tar.gz) | 5.491 MiB |
| `dictionaries` | 13 | [dictionaries-3ebaa990eb35.tar.gz](dist/dictionaries-3ebaa990eb35.tar.gz) | 6.218 MiB |
| `html` | 306 | [html-27b05c89b1ed.tar.gz](dist/html-27b05c89b1ed.tar.gz) | 15.010 MiB |
| `pdf` | 5 | [pdf-d8292e360209.tar.gz](dist/pdf-d8292e360209.tar.gz) | 6.191 MiB |
| `tokenizers` | 2 | [tokenizers-7c48be6322b6.tar.gz](dist/tokenizers-7c48be6322b6.tar.gz) | 3.799 MiB |

5 categories, 327 packaged source files. Release tag: `infra-resources-2026-10-09`.

See `SHA256SUMS` for source-file checksums, `RELEASE_SHA256SUMS` for archive checksums, and `bundles.json` for complete inventories and download URLs. Category archives have no extra wrapper directory.

The HTML package contains 152 fixed HTML inputs, their capture sidecars, an index, and an archive README. Sources reside in `assets/html/`; both that directory and `dist/` are excluded from Git. infra uses a URL and full-SHA256 lock, reuses its verified download cache, and does not recapture source sites.

See `assets.json`, `licenses/`, and the category documentation for provenance and licensing. Packaging does not grant a uniform license to website content.

These release notes are generated locally; consult the Release for actual attachment availability. Before publication, run `python3 pack.py --check`, then upload category archives and updated manifests. Retain previously published attachments.
