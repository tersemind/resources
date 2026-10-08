#!/usr/bin/env python3
# Copyright (C) TerseMind.
# Use of this source code is governed by an MIT license.
"""Pack each assets/ category into one deterministic release archive (Python 3.9+)."""

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('categories', nargs='*', help='categories to repack; default: every assets/ directory')
    args = parser.parse_args()
    try:
        categories = {p.name: p for p in sorted((ROOT / 'assets').iterdir()) if p.is_dir() and not p.is_symlink()}
        selected = list(dict.fromkeys(args.categories)) if args.categories else list(categories)
        unknown = set(selected) - categories.keys()
        if unknown:
            raise ValueError('Unknown categories: ' + ', '.join(sorted(unknown)))
        metadata = json.loads((ROOT / 'assets.json').read_text())
        index_path = ROOT / 'bundles.json'
        old = json.loads(index_path.read_text()) if index_path.exists() else {'bundles': []}
        bundles = {b['category']: b for b in old['bundles'] if b['category'] in categories}
        members = {}
        for category, directory in categories.items():
            files = sorted(p for p in directory.rglob('*') if p.is_file())
            if any(p.is_symlink() for p in directory.rglob('*')):
                raise ValueError(f'{category}: symlinks are not supported')
            if not files:
                raise ValueError(f'{category}: category is empty')
            members[category] = [
                {'path': p.relative_to(ROOT).as_posix(), 'archive_path': p.relative_to(directory).as_posix(),
                 'sha256': sha256(p), 'size_bytes': p.stat().st_size} for p in files]
            if category not in selected and category not in bundles:
                raise ValueError(f'{category}: no package yet; run without category arguments first')
            if category not in selected and bundles[category]['members'] != members[category]:
                raise ValueError(f'{category}: files changed; include this category in the update')
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
                # Only remove the superseded local output registered by this tool.
                # Published release assets and other historical files are untouched.
                if previous and previous['path'] != bundles[category]['path']:
                    old_path = ROOT / previous['path']
                    if old_path.parent == dist and old_path.is_file():
                        old_path.unlink()
                print(f'{category}: {len(members[category])} files -> {filename}')
        ordered = [bundles[name] for name in sorted(bundles)]
        for bundle in ordered:
            bundle['release_url'] = f"https://github.com/{metadata['repository']}/releases/download/{metadata['release_tag']}/{bundle['release_asset']}"
        index_path.write_text(json.dumps({'schema_version': 1, 'release_tag': metadata['release_tag'], 'bundles': ordered}, indent=2) + '\n')
        (ROOT / 'SHA256SUMS').write_text(''.join(m['sha256'] + '  ' + m['path'] + '\n' for category in sorted(members) for m in members[category]))
        (ROOT / 'RELEASE_SHA256SUMS').write_text(''.join(b['sha256'] + '  ' + b['release_asset'] + '\n' for b in ordered))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
