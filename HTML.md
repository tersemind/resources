# HTML fixture resource package

The current local package covers all 152 fixed HTML fixtures in infra: 49 from the original resource package and 103 frozen supplemental regression samples. It was packaged on 2026-10-17, with all HTML and capture-sidecar bytes preserved. No pages were recaptured, assertions changed, or failing samples removed. This English documentation update changes the archive README and therefore produces a new content-addressed package.

Resource payloads reside in assets/html/ and archives in dist/; both are excluded from Git. The package contains 306 files: 152 input pairs, an index, and a README.

## Local package and publication status

Current local package: [html-27b05c89b1ed.tar.gz](dist/html-27b05c89b1ed.tar.gz).

- Full SHA256: `27b05c89b1ed5d37c04313760b3f6d103f44ff53a73820fa18d5ab14bac7c5dc`.
- Index SHA256: `c2c61e429781d7b027cbe9a2a453aa7e65f7bd671d6998eec1e707492ba98320`.
- The new package has not been uploaded; release_url in bundles.json is a publication target.
- The previously uploaded html-1f1b115ae388.tar.gz attachment remains unchanged. Local historical packages, including html-e65cb9df9bd1.tar.gz, are also retained.
- infra still uses its previous download lock and supplemental manifest. It does not point to the unpublished package.

## Consumption and migration

1. Run pack.py --check in resources to verify all categories and manifests.
2. Upload the new archive and updated resource manifests, retaining previous attachments.
3. Update the bundle URL, full SHA256, size, and index_sha256 in infra's corpus.lock.json. Remove the supplemental reference whose inputs are now included in this package; preserve fixture inputs, assertions, and dataset splits.
4. Restore through the new lock into an empty output directory. Verify all 152 inputs and capture identities, then run strict-input, coverage, and Eval calibration checks.

Both downloads and offline --archive restoration verify the complete hash lock. Supplying a new --archive while retaining the old lock correctly rejects the new package. An isolated lock and empty directory have been used to verify that this package independently restores every sample. Switch the production download lock only after upload.

## Provenance and scope

index.json records the previous index hash, supplemental-manifest hash, current fixtures.json hash, and each sample's URL, HTML byte size, and two file hashes. The 103 supplemental inputs retain their frozen contents; capture times, statuses, and response headers are not invented. Legacy URL/hash bindings do not prove that the sidecar and HTML came from the same capture. Browser HTML is replayed as UTF-8; available response metadata remains in the original .input.json.

infra retains assertions, rules, Eval calibration, and derived parser outputs; they are not included as raw inputs. These samples have been used for development or tuning and are not an independent private protection set. Website content retains its respective rights, and repackaging does not grant a uniform license.
