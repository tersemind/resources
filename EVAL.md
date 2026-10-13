# Public Eval calibration fixture

The local Eval package contains 20 frozen HTML/native Doc pairs for 10 annotated baseline/mutated cases, plus manifest.json and checks.json. The 42 declared files are stored under assets/eval/ and packaged without a wrapper directory. Payloads and dist/ remain excluded from Git; bundles.json and checksum manifests record every member.

## Current state

- Package: [eval-032c00ea45f6.tar.gz](dist/eval-032c00ea45f6.tar.gz), 8,780,047 bytes.
- Archive SHA256: `032c00ea45f68602af167706660edea98273fd01d0cd0edac43b387f6de084bc`.
- Manifest SHA256: `ec9fde39294b5dfb6c3a5f07dc99dc81b9e99be5c74d30e8a96eeb6201d957f4`.
- Checks SHA256: `bd713d6df1455b6bf5e1bafd6791b93d4c9da0037dc25e741f594dfe71ec5073`.
- The corrected package is local only; its release_url is a publication target. The original `eval-19bacd69c93a.tar.gz` archive was published and verified on 2026-10-18.
- The resources eval-fixture.lock.json describes the corrected local archive and retains the original import hashes and selection scope. Infra retains the published predecessor lock until a new upload is authorized and verified.

All original HTML and Doc bytes are preserved. The label revision corrects the stale title expectation against source title evidence and removes a repaired glued-boundary known_miss. assets.json records the predecessor lock, original source URLs and selection provenance. The original import retained all 10 labelled pairs and excluded 9,847 unlabelled benchmark inputs. Original package attachments remain unchanged.

## Maintenance

Validate native manifest/check bindings and all declared source/Doc hashes with infra's eval_fixture inventory before packaging. Run `python3 pack.py eval`, then `python3 pack.py --check`. The generic packer verifies registered member hashes and archive contents; native Eval assertion validation remains in infra. Do not add undeclared files or a README inside assets/eval/.

Infra's eval_fixture_resources Bazel repository rule consumes its own lock. The :inputs target provides frozen HTML/Doc, while :calibration includes checks. Fixtures and worker targets carry these as data/runfiles; worker deployment carries them under res/eval/. Replaying these inputs requires no source-site request or parser rerun.

After an explicitly authorized upload, verify the remote archive hash and update infra's eval-fixture.lock.json with the matching archive, manifest and checks identities. Until publication, keep the existing download lock. This local synchronization does not publish parser rules or model-generated candidates.

## Scope and provenance

These public development/calibration inputs were already used for tuning. They are not the complete HTML fixture corpus, an independent private quality set, or a new stratified annotated dataset. A calibration or no-regression receipt alone does not approve a parser/rules release.

Source canonical identities remain in the frozen Doc files and input hashes in manifest.json; rights follow the original websites, as described in [HTML provenance](licenses/html-fixtures.md). HTML, native Doc and checks are separately hashed. Repackaging does not establish new capture timestamps or confer a uniform website-content license.
