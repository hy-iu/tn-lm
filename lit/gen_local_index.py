#!/usr/bin/env python3
"""Refresh local asset matches: python3 lit/gen_local_index.py [--repos PATH]."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repos', type=Path, default=Path.home() / 'repos')
args = parser.parse_args()
repos, papers = {}, {}
for folder in sorted(args.repos.expanduser().iterdir()):
    if not folder.is_dir():
        continue
    result = subprocess.run(['git', '-C', str(folder), 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    match = re.search(r'github\.com[:/]([^/]+/[^\s]+)', result.stdout)
    key = match[1].removesuffix('.git').lower() if match else None
    asset = {'label': '本地代码 · ' + folder.name, 'path': str(folder.resolve()), 'href': folder.resolve().as_uri() + '/'}
    if key:
        repos.setdefault(key, []).append(asset)
    # Explicit paper references in root READMEs connect implementations to papers.
    for readme in folder.glob('*'):
        if readme.is_file() and readme.name.lower().startswith('readme'):
            content = readme.read_text(errors='replace')
            for arxiv in set(re.findall(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})', content)):
                papers.setdefault(arxiv, []).append({**asset, 'label': '本地仓库引用 · ' + folder.name})
archive = ROOT / 'lit/arxiv_papers'
for entry in sorted(archive.iterdir()):
    match = re.match(r'(\d{4}\.\d{4,5})(?!\d)', entry.name)
    if not match or (not entry.is_dir() and entry.suffix.lower() != '.pdf'):
        continue
    label = '本地中文' if '_zh' in entry.name or '粗调' in entry.name else '本地原文'
    label += '源码' if entry.is_dir() else ' PDF'
    papers.setdefault(match[1], []).append({'label': label + ' · ' + entry.name, 'path': './' + str(entry.relative_to(ROOT)), 'href': '../' + str(entry.relative_to(ROOT)) + ('/' if entry.is_dir() else '')})
data = {'repos': repos, 'papers': papers}
(ROOT / 'app/local-index-data.js').write_text('window.LOCAL_INDEX = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')
print(f'Indexed {len(repos)} repository origins and {len(papers)} arXiv IDs')
