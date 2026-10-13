#!/usr/bin/env python3
# Copyright (C) TerseMind.
# Use of this source code is governed by an MIT license.
"""Pack or verify registered resource categories (Python 3.9+)."""

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parent


def scratch_root():
    # Use infra's shared path interface while this repo lives inside infra.
    for parent in ROOT.parents:
        interface = parent / 'bd/paths/paths.py'
        if interface.is_file():
            spec = importlib.util.spec_from_file_location('infra_paths', interface)
            module = importlib.util.module_from_spec(spec)
            previous = sys.dont_write_bytecode
            sys.dont_write_bytecode = True
            try:
                spec.loader.exec_module(module)
            finally:
                sys.dont_write_bytecode = previous
            return module.scratch_root()
    # The resources repository can also be used independently.
    root = Path(os.environ.get('INFRA_TMP_ROOT', '/tmp/tersemind_infra'))
    if not root.is_absolute() or '..' in root.parts or root == Path('/'):
        raise ValueError('INFRA_TMP_ROOT must be an absolute non-root directory')
    if root.is_symlink() or root.resolve() == ROOT or ROOT in root.resolve().parents:
        raise ValueError('scratch directory must be outside the repository')
    root.mkdir(parents=True, exist_ok=True)
    return root


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def relative(value):
    if not isinstance(value, str) or not value or any(ord(c) < 32 for c in value) or value.startswith('/') or any(part in ('', '.', '..') for part in value.split('/')):
        raise ValueError(f'unsafe resource path: {value}')
    return Path(value)


def local_path(value):
    path = ROOT / relative(value)
    if any(parent.is_symlink() for parent in [path, *path.parents] if parent == ROOT or ROOT in parent.parents):
        raise ValueError(f'symlink resource path: {value}')
    return path


def html_snapshot(directory):
    index = json.loads((directory / 'index.json').read_text())
    if index.get('version') != 1 or not index.get('samples'):
        raise ValueError('unsupported or empty HTML index')
    expected = set()
    names = set()
    for sample in index['samples']:
        html = relative(sample['html'])
        capture = relative(sample['capture'])
        if len(html.parts) != 1 or len(capture.parts) != 1 or html.suffix != '.html' or capture != html.with_suffix('.input.json'):
            raise ValueError('HTML inputs must use flat, paired filenames')
        if str(html) in expected or sample['name'] in names or not sample.get('available', True):
            raise ValueError('duplicate or unavailable HTML fixture')
        names.add(sample['name'])
        expected.update((str(html), str(capture)))
        source = directory / 'inputs' / html
        context_path = directory / 'inputs' / capture
        if sha256(source) != sample['html_sha256'] or source.stat().st_size != sample['bytes']:
            raise ValueError(f'HTML digest/size differs from index: {html}')
        if sha256(context_path) != sample['capture_sha256']:
            raise ValueError(f'capture digest differs from index: {capture}')
        context = json.loads(context_path.read_text())
        if context.get('url') != sample['url'] or context.get('html_sha256') != sample['html_sha256']:
            raise ValueError(f'capture identity differs from index: {capture}')
    actual = {p.name for p in (directory / 'inputs').iterdir() if p.is_file()}
    if actual != expected or any(not p.is_file() for p in (directory / 'inputs').iterdir()):
        raise ValueError('HTML input inventory differs from index')


def inventory(category, directory, source_format=None):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', category):
        raise ValueError(f'unsafe category: {category}')
    paths = sorted(directory.rglob('*'))
    if any(p.is_symlink() for p in paths):
        raise ValueError(f'{category}: symlinks are not supported')
    files = [p for p in paths if p.is_file()]
    if not files:
        raise ValueError(f'{category}: category is empty')
    if source_format == 'html-fixtures-v1':
        html_snapshot(directory)
    elif source_format:
        raise ValueError(f'unsupported category format: {source_format}')
    return [{'path': p.relative_to(ROOT).as_posix(), 'archive_path': p.relative_to(directory).as_posix(),
             'sha256': sha256(p), 'size_bytes': p.stat().st_size} for p in files]


def archive_check(bundle):
    path = local_path(bundle['path'])
    if sha256(path) != bundle['sha256'] or path.stat().st_size != bundle['size_bytes']:
        raise ValueError(f"{bundle['category']}: archive checksum/size mismatch")
    expected = {m['archive_path']: m for m in bundle['members']}
    seen = set()
    with tarfile.open(path, 'r|gz') as archive:
        for member in archive:
            relative(member.name)
            if not member.isfile() or member.name in seen or member.name not in expected:
                raise ValueError(f'unsafe or unexpected archive member: {member.name}')
            record = expected[member.name]
            digest = hashlib.sha256()
            stream = archive.extractfile(member)
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
            if member.size != record['size_bytes'] or digest.hexdigest() != record['sha256']:
                raise ValueError(f'archive member digest mismatch: {member.name}')
            seen.add(member.name)
    if seen != set(expected):
        raise ValueError('archive members missing')


def generated(metadata, ordered):
    table = '| Category | Archive files | Package | Compressed size |\n| --- | ---: | --- | ---: |\n'
    for b in ordered:
        table += f"| `{b['category']}` | {len(b['members'])} | [{b['release_asset']}]({b['path']}) | {b['size_bytes'] / (1 << 20):.3f} MiB |\n"
    table += f"\n{len(ordered)} categories, {sum(len(b['members']) for b in ordered)} packaged source files. Release tag: `{metadata['release_tag']}`.\n"
    readme = (ROOT / 'README.md').read_text()
    pattern = r'<!-- BEGIN GENERATED BUNDLES -->.*?<!-- END GENERATED BUNDLES -->'
    replacement = '<!-- BEGIN GENERATED BUNDLES -->\n' + table + '<!-- END GENERATED BUNDLES -->'
    if len(re.findall(pattern, readme, re.S)) != 1:
        raise ValueError('README requires one generated bundle table')
    readme = re.sub(pattern, lambda _: replacement, readme, flags=re.S)
    release = f"# Infra resources — {metadata['snapshot_date']}\n\n" + table
    release += '\nSee `SHA256SUMS` for source-file checksums, `RELEASE_SHA256SUMS` for archive checksums, and `bundles.json` for complete inventories and download URLs. Category archives have no extra wrapper directory.\n'
    html = next((b for b in ordered if b['category'] == 'html'), None)
    if html:
        count = sum(m['archive_path'].endswith('.html') for m in html['members'])
        release += f'\nThe HTML package contains {count} fixed HTML inputs, their capture sidecars, an index, and an archive README. Sources reside in `assets/html/`; both that directory and `dist/` are excluded from Git. infra uses a URL and full-SHA256 lock, reuses its verified download cache, and does not recapture source sites.\n'
    release += '\nSee `assets.json`, `licenses/`, and the category documentation for provenance and licensing. Packaging does not grant a uniform license to website content.\n\nThese release notes are generated locally; consult the Release for actual attachment availability. Before publication, run `python3 pack.py --check`, then upload category archives and updated manifests. Retain previously published attachments.\n'
    sums = ''.join(m['sha256'] + '  ' + m['path'] + '\n' for b in ordered for m in b['members'])
    release_sums = ''.join(b['sha256'] + '  ' + b['release_asset'] + '\n' for b in ordered)
    return {'README.md': readme, 'RELEASE.md': release, 'SHA256SUMS': sums, 'RELEASE_SHA256SUMS': release_sums}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('categories', nargs='*', help='categories to repack; default: all available source directories')
    parser.add_argument('--check', action='store_true', help='verify sources, archives and generated manifests without changing files')
    args = parser.parse_args(argv)
    try:
        metadata = json.loads((ROOT / 'assets.json').read_text())
        index_path = ROOT / 'bundles.json'
        old = json.loads(index_path.read_text()) if index_path.exists() else {'bundles': []}
        bundles = {b['category']: b for b in old['bundles']}
        if len(bundles) != len(old['bundles']):
            raise ValueError('duplicate registered bundle category')
        assets = local_path('assets')
        categories = {p.name: local_path(p.relative_to(ROOT).as_posix()) for p in sorted(assets.iterdir()) if p.is_dir()} if assets.is_dir() else {}
        formats = metadata.get('category_formats', {})
        if metadata.get('category_sources'):
            raise ValueError('category sources must be under assets/<category>')
        selected = list(dict.fromkeys(args.categories)) if args.categories else sorted(bundles if args.check else categories)
        unknown = set(selected) - (categories.keys() | bundles.keys())
        if unknown:
            raise ValueError('Unknown categories: ' + ', '.join(sorted(unknown)))
        for category in selected:
            if category not in categories or not categories[category].is_dir():
                raise ValueError(f'{category}: sources unavailable; restore the registered package first')
        generated(metadata, [bundles[name] for name in sorted(bundles)])
        members = {}
        for category, directory in categories.items():
            members[category] = inventory(category, directory, formats.get(category))
            if category not in selected and category not in bundles:
                raise ValueError(f'{category}: no package yet; run without category arguments first')
            if (args.check or category not in selected) and bundles.get(category, {}).get('members') != members[category]:
                raise ValueError(f'{category}: files changed; include this category in the update')
        available_members = {m['path']: m for group in members.values() for m in group}
        for asset in metadata.get('assets', []):
            for record in [asset, *asset.get('members', [])]:
                current = available_members.get(record.get('path'))
                if current and record.get('sha256') and (record['sha256'] != current['sha256'] or record.get('size_bytes', current['size_bytes']) != current['size_bytes']):
                    raise ValueError(f"source record differs from actual file: {record['path']}")
        for category in bundles.keys() - categories.keys():
            print(f'{category}: unavailable locally; retained registered metadata (not verified)')
        if args.check:
            for category in selected:
                archive_check(bundles[category])
            ordered = [bundles[name] for name in sorted(bundles)]
            if old.get('release_tag') != metadata['release_tag']:
                raise ValueError('release tag differs from bundle index')
            for bundle in ordered:
                url = f"https://github.com/{metadata['repository']}/releases/download/{metadata['release_tag']}/{bundle['release_asset']}"
                if bundle['release_url'] != url:
                    raise ValueError('release URL differs from metadata')
            for name, text in generated(metadata, ordered).items():
                if (ROOT / name).read_text() != text:
                    raise ValueError(f'{name}: generated manifest differs')
            print('verified categories: ' + ', '.join(selected))
            return 0
        dist = ROOT / 'dist'
        dist.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='resources-pack-', dir=scratch_root()) as directory:
            for category in selected:
                temporary = Path(directory) / f'{category}.tar.gz'
                with temporary.open('wb') as output, gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0) as compressed, tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as archive:
                    for member in members[category]:
                        path = ROOT / member['path']
                        info = tarfile.TarInfo(member['archive_path'])
                        info.size = member['size_bytes']
                        info.mode = 0o644
                        info.uid = info.gid = info.mtime = 0
                        with path.open('rb') as source:
                            archive.addfile(info, source)
                # Catch edits made while packing, before publishing a local output.
                if any(sha256(ROOT / m['path']) != m['sha256'] for m in members[category]):
                    raise ValueError(f'{category}: files changed during packing; rerun')
                digest = sha256(temporary)
                filename = f'{category}-{digest[:12]}.tar.gz'
                path = dist / filename
                previous = bundles.get(category)
                shutil.copyfile(temporary, path)
                bundles[category] = {
                    'category': category, 'path': path.relative_to(ROOT).as_posix(),
                    'release_asset': filename, 'sha256': digest, 'size_bytes': path.stat().st_size,
                    'release_url': f"https://github.com/{metadata['repository']}/releases/download/{metadata['release_tag']}/{filename}",
                    'members': members[category],
                }
                # Preserve a recoverable copy of a superseded generated output.
                if previous and previous['path'] != bundles[category]['path']:
                    old_path = ROOT / previous['path']
                    if old_path.parent == dist and old_path.is_file():
                        backup = scratch_root() / 'resources-pack-history'
                        backup.mkdir(exist_ok=True)
                        shutil.move(str(old_path), str(backup / old_path.name))
                print(f'{category}: {len(members[category])} files -> {filename}')
        ordered = [bundles[name] for name in sorted(bundles)]
        for bundle in ordered:
            bundle['release_url'] = f"https://github.com/{metadata['repository']}/releases/download/{metadata['release_tag']}/{bundle['release_asset']}"
        index_path.write_text(json.dumps({'schema_version': 1, 'release_tag': metadata['release_tag'], 'bundles': ordered}, indent=2) + '\n')
        for name, text in generated(metadata, ordered).items():
            (ROOT / name).write_text(text)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
