#!/usr/bin/env python3
"""Resource packaging and immutable HTML identity regression tests."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pack


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()


class PackTests(unittest.TestCase):
    def setUp(self):
        base = Path('/tmp/tersemind_infra/resource-pack-tests')
        base.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.addCleanup(patch.stopall)
        patch.object(pack, 'ROOT', self.root).start()
        patch.object(pack, 'scratch_root', return_value=base).start()
        (self.root / 'assets/other').mkdir(parents=True)
        (self.root / 'assets/other/data.txt').write_bytes(b'unchanged dependency')
        inputs = self.root / 'assets/html/inputs'
        inputs.mkdir(parents=True)
        html = b'<html><p>fixed article</p></html>'
        self.url = 'https://example.test/article'
        self.context = {'url': self.url, 'html_sha256': hashlib.sha256(html).hexdigest()}
        (inputs / 'article.html').write_bytes(html)
        (inputs / 'article.input.json').write_bytes(encoded(self.context))
        self.index = {'version': 1, 'samples': [{'name': 'article', 'html': 'article.html', 'capture': 'article.input.json',
            'url': self.url, 'bytes': len(html), 'html_sha256': self.context['html_sha256'],
            'capture_sha256': hashlib.sha256(encoded(self.context)).hexdigest()}]}
        (self.root / 'assets/html/index.json').write_bytes(encoded(self.index))
        (self.root / 'assets/html/README.md').write_text('Fixed fixture inputs\n')
        (self.root / 'README.md').write_text('# Resources\n<!-- BEGIN GENERATED BUNDLES -->\n<!-- END GENERATED BUNDLES -->\n')
        (self.root / 'assets.json').write_bytes(encoded({'repository': 'example/resources', 'release_tag': 'snapshot-1',
            'snapshot_date': '2026-10-13', 'assets': [],
            'category_formats': {'html': 'html-fixtures-v1'}}))

    def run_pack(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return pack.main(list(args))

    def bundles(self):
        return {b['category']: b for b in json.loads((self.root / 'bundles.json').read_text())['bundles']}

    def test_html_repack_is_deterministic_and_all_manifests_verify(self):
        self.assertEqual(self.run_pack(), 0)
        before = self.bundles()
        (self.root / 'assets/html/inputs/article.html').touch()
        self.assertEqual(self.run_pack('html'), 0)
        self.assertEqual(self.bundles(), before)
        self.assertEqual(self.run_pack('--check'), 0)
        self.assertIn('assets/html/index.json', (self.root / 'SHA256SUMS').read_text())
        self.assertIn(before['html']['release_asset'], (self.root / 'RELEASE_SHA256SUMS').read_text())
        self.assertIn(before['html']['release_asset'], (self.root / 'README.md').read_text())
        self.assertIn('HTML package contains 1 fixed HTML input', (self.root / 'RELEASE.md').read_text())

    def test_html_only_update_preserves_unmaterialized_categories(self):
        self.assertEqual(self.run_pack(), 0)
        before = self.bundles()['other']
        (self.root / 'assets/other').rename(self.root / 'original-other')
        self.assertEqual(self.run_pack('html'), 0)
        self.assertEqual(self.bundles()['other'], before)
        self.assertEqual(self.run_pack('--check', 'html'), 0)
        self.assertEqual(self.run_pack('--check'), 2)

    def test_bad_html_digest_is_rejected_before_manifests_change(self):
        self.assertEqual(self.run_pack(), 0)
        before = (self.root / 'bundles.json').read_bytes()
        (self.root / 'assets/html/inputs/article.html').write_bytes(b'new live page')
        self.assertEqual(self.run_pack('html'), 2)
        self.assertEqual((self.root / 'bundles.json').read_bytes(), before)

    def test_mixed_capture_identity_is_rejected(self):
        self.context['url'] = 'https://other.test/page'
        raw = encoded(self.context)
        (self.root / 'assets/html/inputs/article.input.json').write_bytes(raw)
        self.index['samples'][0]['capture_sha256'] = hashlib.sha256(raw).hexdigest()
        (self.root / 'assets/html/index.json').write_bytes(encoded(self.index))
        self.assertEqual(self.run_pack(), 2)
        self.assertFalse((self.root / 'bundles.json').exists())

    def test_unregistered_input_and_symlink_and_traversal_are_rejected(self):
        extra = self.root / 'assets/html/inputs/extra.html'
        extra.write_text('unregistered')
        self.assertEqual(self.run_pack(), 2)
        extra.unlink()
        extra.symlink_to(self.root / 'assets/other/data.txt')
        self.assertEqual(self.run_pack(), 2)
        extra.unlink()
        self.index['samples'][0]['html'] = '../article.html'
        (self.root / 'assets/html/index.json').write_bytes(encoded(self.index))
        self.assertEqual(self.run_pack(), 2)

    def test_stale_source_registry_record_is_rejected(self):
        path = self.root / 'assets.json'
        metadata = json.loads(path.read_text())
        metadata['assets'] = [{'path': 'assets/html/index.json', 'sha256': '0' * 64}]
        path.write_bytes(encoded(metadata))
        self.assertEqual(self.run_pack(), 2)
        self.assertFalse((self.root / 'bundles.json').exists())

    def test_unselected_changed_dependency_fails(self):
        self.assertEqual(self.run_pack(), 0)
        (self.root / 'assets/other/data.txt').write_text('changed')
        self.assertEqual(self.run_pack('html'), 2)

    def test_corrupt_archive_and_checksum_manifest_fail_read_only_check(self):
        self.assertEqual(self.run_pack(), 0)
        archive = self.root / self.bundles()['html']['path']
        original = archive.read_bytes()
        archive.write_bytes(b'corrupt')
        self.assertEqual(self.run_pack('--check', 'html'), 2)
        archive.write_bytes(original)
        (self.root / 'SHA256SUMS').write_text('incorrect ledger\n')
        self.assertEqual(self.run_pack('--check', 'html'), 2)


if __name__ == '__main__':
    unittest.main()
