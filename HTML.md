# HTML fixture input package

The local package contains 1,296 frozen HTML inputs, their capture sidecars, an index and a package README (2,594 files). The 178 pairs from the previous local package retain their exact bytes; the 1,118 additional pairs come from the existing infra fixture inventory and were not recaptured. Assertions and rules remain in infra.

## Package identity

- Archive: [html-4d221b255050.tar.gz](dist/html-4d221b255050.tar.gz)
- SHA256: `4d221b2550500a9c800da24a387f8d2ef938efb5b22de80dbf4066e62da86305`
- Size: 59,388,830 bytes
- Index SHA256: `6ce217c58d6913359cee93b005177fbe54a247ba0eae8847f8554a78ae6aed49`
- Infra fixtures manifest SHA256: `e122a6bbdb1d7ba19f965ed7c4531e13380295a762f8480f8610716af94dda0c`

The package was validated locally with `python3 pack.py html --check` and a clean-directory restore and recheck of all 1,296 pairs. The new archive's Release availability has not been verified. Keep infra's currently pinned Release lock and existing attachments until the new archive is published and verified; remove the supplemental reference only when updating the lock to this complete package.

These fixtures have been used for development and tuning and are not an independent protection set. Capture metadata is preserved without inventing timestamps or headers. Source-site content retains its original rights.
