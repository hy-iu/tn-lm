#!/usr/bin/env python3
"""Build citation previews and explicit paragraph groups from reviewed source data."""
import hashlib
import html as html_module
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
page_path = ROOT / 'app/index.html'
html = page_path.read_text()
library = (ROOT / 'app/library.html').read_text()
papers = json.loads(re.search(r'^const PAPERS=(.*);$', library, re.M)[1])
extras = json.loads((ROOT / 'lit/audit/memo_extra_papers.json').read_text())
manifest = json.loads((ROOT / 'lit/audit/memo_citation_map.json').read_text())

def norm(text):
    return ''.join(c for c in html_module.unescape(text).casefold() if c.isalnum())

def arxiv_ids(text):
    return set(re.findall(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})(?!\d)', text, re.I))

def links_unique(links):
    return [[label, url] for url, label in dict((url, label) for label, url in reversed(links)
            if url.startswith(('https://', 'http://'))).items()][::-1]

def paper_ref(p, key):
    return {'key': key, 'title': p['t'], 'authors': p['a'], 'venue': p['v'], 'year': p['y'],
            'library': 'library.html#paper=' + quote(p['u'], safe=''),
            'aliases': [p['t'], *sorted(arxiv_ids(p['u'] + ' ' + str(p['lk'])))],
            'links': links_unique([['论文', p['u']], *p['lk']])}

refs = []
by_url = {}
# Distinct method names are safe fallback aliases; author surnames are not.
aliases = {'p07': ['TensorGPT'], 'p08': ['CompactifAI'], 'p09': ['L²M'],
           'p10': ['TensorLLM'], 'p11': ['Saten'], 'p13': ['Minima'],
           'p17': ['M²RNN'], 'p19': ['MQAR'], 'p20': ['TTLM'],
           'p21': ['Gather-and-Aggregate'], 'p22': ['KroneckerBERT', 'KnGPT']}
for pid, block in re.findall(r'<div class="paper" id="(p\d+)">(.*?)(?=<div class="paper"|</section>)', html, re.S):
    title = re.search(r'class="p-title">(.*?)</span>', block)[1]
    urls = re.findall(r'href="(https?://[^"]+)"', block)
    canonical_title = {'p15': 'Tensor networks and efficient descriptions of classical data'}.get(pid, title)
    title_matches = [p for p in papers if norm(p['t']) == norm(canonical_title)]
    matched = title_matches or [p for p in papers if p['u'] in urls or any(
        arxiv_ids(u) & arxiv_ids(p['u'] + ' ' + str(p['lk'])) for u in urls)]
    if matched:
        p = matched[0]
        ref = paper_ref(p, pid)
        ref['links'] = links_unique(ref['links'] + [['论文', u] for u in urls])
        by_url[p['u']] = ref
    else:
        ref = {'key': pid, 'title': title, 'aliases': [title, *sorted(arxiv_ids(' '.join(urls)))],
               'year': re.search(r'class="p-year">(.*?)</span>', block)[1],
               'venue': re.search(r'class="p-venue">(.*?)</span>', block)[1],
               'links': links_unique([['论文', u] for u in urls])}
    ref['id'] = pid
    ref['aliases'].extend(aliases.get(pid, []))
    refs.append(ref)

reviewed = json.loads((ROOT / 'lit/audit/memo_paper_additions.json').read_text())
for p in reviewed['papers']:
    ref = next(r for r in refs if r.get('id') == p['id'])
    ref.update({k: p[k] for k in ['authors', 'venue', 'year', 'title']})
    ref['aliases'].append(p['arxiv'])

code_links = {'p03': 'https://github.com/congzlwag/UnsupGenModbyMPS',
              'p05': 'https://github.com/jemisjoky/umps_code',
              'p10': 'https://github.com/guyuxuan9/TensorLLM',
              'p11': 'https://github.com/rmsolgi/saten',
              'p12': 'https://github.com/haotong-Duan/UnitaryMPS-SpaceDecoupling'}
for ref in refs:
    url = code_links.get(ref.get('id'))
    if url and not any(u.lower() == url.lower() for _, u in ref['links']):
        ref['links'].append(['GitHub', url])

by_key = {r['key']: r for r in refs}
extra_keys = {p['u']: p['key'] for p in extras}
def resolve(selector):
    if selector in by_key:
        return by_key[selector]
    selector = next((p['t'] for p in extras if p['key'] == selector), selector)
    matches = [p for p in papers if norm(p['t']) == norm(selector)]
    if not matches:
        matches = [p for p in papers if norm(p['t']).startswith(norm(selector))]
    if len(matches) != 1:
        raise ValueError(f'Citation must resolve uniquely: {selector!r} ({len(matches)} matches)')
    p = matches[0]
    if p['u'] in by_url:
        return by_url[p['u']]
    key = extra_keys.get(p['u'], 'bib-' + hashlib.sha256(p['u'].encode()).hexdigest()[:12])
    ref = paper_ref(p, key)
    refs.append(ref)
    by_key[key] = ref
    by_url[p['u']] = ref
    return ref

for rule in manifest['rules']:
    rule['keys'] = [resolve(selector)['key'] for selector in rule['references']]

# Merged publication/preprint records retain their old URLs as links. Migrate
# existing paragraph selectors to the canonical reference instead of losing it.
key_redirects = {'bib-' + hashlib.sha256(url.encode()).hexdigest()[:12]: ref['key']
                 for ref in refs for _, url in ref['links']}

# The author-labelled prose is reviewed explicitly. Each paragraph retains one icon.
body, rest = html.split('<section id="papers">', 1)
counts = [0] * len(manifest['rules'])
def annotate(match):
    tag, attrs, content = match.groups()
    text = html_module.unescape(re.sub(r'<[^>]+>', '', content))
    old = re.search(r'\bdata-refs="([^"]*)"', attrs)
    keys = [key if key in by_key else key_redirects.get(key, key)
            for key in old[1].split()] if old else []
    for i, rule in enumerate(manifest['rules']):
        if norm(rule['mention']) in norm(text):
            counts[i] += 1
            keys.extend(rule['keys'])
    if keys:
        attrs = re.sub(r'\s*data-refs="[^"]*"', '', attrs)
        attrs += ' data-refs="' + ' '.join(dict.fromkeys(keys)) + '"'
    return '<' + tag + attrs + '>' + content + '</' + tag + '>'
body = re.sub(r'<(p|td)\b([^>]*)>(.*?)</\1>', annotate, body, flags=re.S)
missing = [rule['mention'] for rule, count in zip(manifest['rules'], counts) if not count]
if missing:
    raise ValueError('Citation groups no longer found in prose: ' + ', '.join(missing))

# Exact titles and identifiers cover citations in tables without broad author matching.
plain_body = html_module.unescape(re.sub(r'<[^>]+>', ' ', body))
for p in papers:
    if norm(p['t']) in norm(plain_body) or any(aid in plain_body for aid in arxiv_ids(p['u'] + ' ' + str(p['lk']))):
        if p['u'] not in by_url:
            resolve(p['t'])

refs.append({'key': 'tool-nanoinfra', 'title': 'nanoinfra · 本地训练框架', 'aliases': ['nanoinfra'],
             'links': [['GitHub', 'https://github.com/hy-iu/nanoinfra']]})
tools_html = (ROOT / 'app/toolboxes.html').read_text()
tools = json.loads(re.search(r'^const D=(.*);$', tools_html, re.M)[1])
for i, tool in enumerate(tools['tools']):
    if len(tool['n']) >= 5 and tool['n'].casefold() in plain_body.casefold():
        refs.append({'key': 'tool-' + str(i), 'title': tool['n'], 'aliases': [tool['n']], 'links': tool['u']})

(ROOT / 'app/memo-refs-data.js').write_text('window.MEMO_REFS = ' + json.dumps(refs, ensure_ascii=False, indent=2) + ';\n')
page_path.write_text(body + '<section id="papers">' + rest)
report = {'checked_on': manifest['checked_on'], 'groups': [
    {'mention': rule['mention'], 'matched_blocks': count, 'references': [by_key[key]['title'] for key in rule['keys']]}
    for rule, count in zip(manifest['rules'], counts)]}
(ROOT / 'lit/audit/memo_citation_coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(f'{len(refs)} reference previews; {len(counts)} explicit groups, {sum(counts)} matched blocks')
