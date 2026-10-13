# TerseMind build dependency resources

Resource payloads are organized by type under `assets/` and packaged into `dist/`. Neither directory is tracked by Git. Git stores packaging scripts, provenance and license records, checksum manifests, and documentation. infra consumes packages from pinned GitHub Release URLs and does not require a resources checkout.

The Release tag is `infra-resources-2026-10-09`. The local HTML package contains 1,296 frozen input pairs from the current infra fixture inventory, including the previous 178 pairs unchanged. Packaging does not imply recapture. The new HTML archive's remote availability has not been verified; see [HTML.md](HTML.md). Eval release details are in [EVAL.md](EVAL.md).

## Layout

```text
assets/
  html/               1,296 HTML files, 1,296 capture sidecars, index.json, archive README
  eval/               Frozen Eval HTML/native Doc pairs, manifest.json and checks.json
  corpus/             MSR training corpus
  tokenizers/         DeepSeek and Qwen tokenizer.json files
  pdf/                Original Adobe archives and the fonttools glyph table
  dictionaries/       jieba, Norvig, and THUOCL dictionaries
licenses/             Upstream licenses and provenance notes
dist/                 Generated category archives, excluded from Git
pack.py               Packaging and verification entry point (Python 3.9+)
assets.json           Resource provenance, uses, licenses, and validation formats
bundles.json          Package hashes, download URLs, and member inventories
SHA256SUMS            Checksums of all packaged source files
RELEASE_SHA256SUMS    Checksums of all category archives
HTML.md               HTML package usage and maintenance
EVAL.md               Native Eval fixture identity, packaging and consumption
eval-fixture.lock.json Pinned Eval archive, workload, labels and import provenance
DICTIONARIES.md       Dictionary integration instructions
RELEASE.md            Manual publication notes
```

Each archive starts directly with the contents of its category directory, without an extra wrapper directory. Filenames and index identities under `assets/html/inputs/` remain stable. Moving local directories does not change the bytes or hashes of an already published archive.

## Category packages

<!-- BEGIN GENERATED BUNDLES -->
| Category | Archive files | Package | Compressed size |
| --- | ---: | --- | ---: |
| `corpus` | 1 | [corpus-ab5947391ce6.tar.gz](dist/corpus-ab5947391ce6.tar.gz) | 5.491 MiB |
| `dictionaries` | 13 | [dictionaries-3ebaa990eb35.tar.gz](dist/dictionaries-3ebaa990eb35.tar.gz) | 6.218 MiB |
| `eval` | 42 | [eval-032c00ea45f6.tar.gz](dist/eval-032c00ea45f6.tar.gz) | 8.373 MiB |
| `html` | 2594 | [html-4d221b255050.tar.gz](dist/html-4d221b255050.tar.gz) | 56.638 MiB |
| `pdf` | 5 | [pdf-d8292e360209.tar.gz](dist/pdf-d8292e360209.tar.gz) | 6.191 MiB |
| `tokenizers` | 2 | [tokenizers-7c48be6322b6.tar.gz](dist/tokenizers-7c48be6322b6.tar.gz) | 3.799 MiB |

6 categories, 2657 packaged source files. Release tag: `infra-resources-2026-10-09`.
<!-- END GENERATED BUNDLES -->

Package names follow `<category>-<first-12-characters-of-content-SHA256>.tar.gz`. Identical content produces the same filename and checksum. The packer moves superseded local outputs into `resources-pack-history/` under the shared temporary root; published attachments remain available. Existing local historical archives are retained during this documentation update.

## Original resources

| Original Bazel repository | Local file | Size | Use |
| --- | --- | ---: | --- |
| `msr_training_corpus` | [msr-training-872a24b0aa82.utf8](assets/corpus/msr-training-872a24b0aa82.utf8) | 16.109 MiB | Build the tw Chinese segmentation dictionary |
| `deepseek_r1_tokenizer` | [deepseek-r1-tokenizer-ecb6f9fc3698.json](assets/tokenizers/deepseek-r1-tokenizer-ecb6f9fc3698.json) | 7.484 MiB | DeepSeek-R1 BPE vocabulary and tokenizer configuration |
| `qwen3_tokenizer` | [qwen3-0.6b-tokenizer-aeb13307a71a.json](assets/tokenizers/qwen3-0.6b-tokenizer-aeb13307a71a.json) | 10.893 MiB | Qwen3-0.6B BPE vocabulary and tokenizer configuration |
| `adobe_agl_aglfn` | [adobe-agl-aglfn-4036a9ca80a62f64f9de4f7321a9a045ad0ecfd6.tar.gz](assets/pdf/adobe-agl-aglfn-4036a9ca80a62f64f9de4f7321a9a045ad0ecfd6.tar.gz) | 0.034 MiB | Adobe Glyph List and ZapfDingbats glyph-name mappings |
| `adobe_cmap_resources` | [adobe-cmap-resources-f5cf3bca7fdfeaceb77aa82847e974f2306c20b4.tar.gz](assets/pdf/adobe-cmap-resources-f5cf3bca7fdfeaceb77aa82847e974f2306c20b4.tar.gz) | 5.283 MiB | PDF CJK character encoding CMaps |
| `adobe_mapping_resources_pdf` | [adobe-mapping-resources-pdf-2dd5e53fb74a01718b9dfd448a0d1cce6fff2aa5.tar.gz](assets/pdf/adobe-mapping-resources-pdf-2dd5e53fb74a01718b9dfd448a0d1cce6fff2aa5.tar.gz) | 1.482 MiB | PDF CID-to-Unicode mappings |
| `adobe_core14_afms` | [adobe-core14-afms-8c892c3c4955.zip](assets/pdf/adobe-core14-afms-8c892c3c4955.zip) | 0.121 MiB | Adobe Core 14 AFM font metrics |
| `fonttools_standard_glyph_order` | [fonttools-standardGlyphOrder-56b543826cb229cb945ea83a61daaca1a61237a1.py](assets/pdf/fonttools-standardGlyphOrder-56b543826cb229cb945ea83a61daaca1a61237a1.py) | 0.006 MiB | The 258 standard Macintosh glyph names for the TrueType post table |

The inventory of the 13 dictionary files is in [DICTIONARIES.md](DICTIONARIES.md). `assets.json` records provenance, uses, and licenses; `bundles.json` records current file hashes and archive paths. Files without a verifiable source commit are versioned by content hash; `master` is not treated as an immutable commit.

## Packaging and updates

```bash
python3 pack.py                 # Package every local category under assets
python3 pack.py html            # Update only the HTML package
python3 pack.py eval            # Package the native Eval fixture
python3 pack.py pdf tokenizers  # Update selected categories
python3 pack.py --check         # Verify sources, archives, documentation, and manifests
shasum -a 256 -c SHA256SUMS
(cd dist && shasum -a 256 -c ../RELEASE_SHA256SUMS)
```

To add a resource type, create `assets/<category>/`. `assets.json.category_formats` selects additional validation rules; there are no special Git source directories. HTML validation checks the index, sizes, hashes, paired files, and URL identities, rejecting missing or extra files, mixed snapshots, and symbolic links.

pack.py updates `bundles.json`, both checksum manifests, the README package table, and RELEASE.md. Maintainers update provenance and license records explicitly; provenance is not inferred from filenames. Categories that are neither selected nor available locally retain their registered metadata and are reported as unverified. Before a complete release, materialize all categories and run `--check` without category arguments.

A fresh checkout does not contain resource payloads. Download the required archives using `bundles.json`, verify their full SHA256 values, and restore their members into `assets/<category>/`. Preserving the exact archived source bytes allows the same package to be reproduced.

## Manual upload

The new HTML archive is a local package; its Release attachment has not been verified. Download URLs in the manifests are publication targets, not proof of availability. After uploading and verifying the archive, update infra's HTML corpus lock and remove supplemental inputs already included in the package. Keep the currently pinned lock and prior attachments until then. The resources copy of eval-fixture.lock.json describes the local Eval package; see EVAL.md for its publication state.

```bash
git add README.md HTML.md EVAL.md eval-fixture.lock.json DICTIONARIES.md RELEASE.md pack.py test_pack.py \
  assets.json bundles.json SHA256SUMS RELEASE_SHA256SUMS licenses
git commit -m "Use Release packages for all resource categories"
# The maintainer pushes the commit and synchronizes Release manifests.
gh release upload infra-resources-2026-10-09 --repo tersemind/resources \
  README.md HTML.md EVAL.md eval-fixture.lock.json RELEASE.md assets.json bundles.json SHA256SUMS RELEASE_SHA256SUMS
```

Do not force-add `assets/` or `dist/` to Git. This update does not commit, push, or upload a Release.

## infra integration

Bazel dependencies use fixed URLs and full SHA256 values, without strip_prefix. infra's `de/fixtures/html/corpus.lock.json` is the sole HTML input lock; both the Bazel repository rule and fixture restoration use that same lock.

`python3 de/fixtures/html/corpus.py restore` downloads and verifies the package once, caching it under `resource-downloads/` in the shared temporary root. Subsequent validation, deployment builds, and worker startup reuse that verified cache. local_deploy passes the directory to Bazel through `--distdir` to avoid repeated downloads. Worker iterations read restored fixed inputs; rule gates do not contact source sites.

The original four Bazel resource URLs and SHA256 values are unchanged. See [DICTIONARIES.md](DICTIONARIES.md) for char/POS integration and [licenses/NOTICES.md](licenses/NOTICES.md) for licensing records. This repository does not include generated dictionary or PDF Rust tables, transitive dependencies, Cargo crate archives, npm packages, or local build tools. Repository-maintained documentation is in English; resource text, source URLs, and upstream license originals retain their original bytes. An English reference translation accompanies the original THUOCL terms.
