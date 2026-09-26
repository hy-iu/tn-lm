#!/usr/bin/env python3
"""对 lit/bibliography.csv 做零额度的摘要一致性全量扫描。

分类口径与云端试点审计一致（见 abstract_audit_pilot24_brief.md）：
  empty            存量摘要为空
  consistent       存量整体是权威源摘要的子串
  truncated_snippet 存量含 … ，且每个 >20 字符片段都能在权威源命中
  partial          仅部分片段命中
  zero_hit         有权威源但一个片段都对不上 —— 需人工/LLM 取证
  no_identifier    无法从本行提取 arXiv id 或 DOI，脚本层面判不了

只使用确定性请求：arXiv id_list 批量 + OpenAlex 小写 DOI 批量 filter。
用法：python3 lit/audit/scan_abstracts.py
"""

import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter

MAILTO = 'audit@example.org'
UA = {'User-Agent': 'Mozilla/5.0 (abstract-scanner)'}
RETRIES = 3


def fetch(url, timeout=60):
    last = None
    for a in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'replace')
        except Exception as e:  # noqa: BLE001 - 网络异常一律重试后放弃
            last = e
            time.sleep(1.5 * (a + 1))
    print('  FAIL %s -> %s' % (url[:90], last), file=sys.stderr)
    return ''


def sq(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


ELLIPSIS = '…'

ARX_FROM_URL = re.compile(r'arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)', re.I)
DOI_FROM_ANY = re.compile(r'\b(10\.\d{4,9}/[^\s"\'<>,)\\]+)', re.I)


def norm_arxiv(aid):
    return re.sub(r'v\d+$', '', (aid or '').strip())


def extract(row):
    """返回 (arxiv_id 或 '', doi 或 '')"""
    aid = (row.get('arxiv_id') or '').strip()
    if not aid:
        for f in ('url', 'pdf_links', 'all_pdfs'):
            m = ARX_FROM_URL.search(row.get(f) or '')
            if m:
                aid = m.group(1)
                break
    doi = ''
    for f in ('url', 'doi', 'journal_ref', 'pdf_links', 'all_pdfs', 'publication_info'):
        m = DOI_FROM_ANY.search(row.get(f) or '')
        if m:
            doi = m.group(1).rstrip('.').lower()
            break
    return norm_arxiv(aid), doi


def openalex_abstract(inv):
    pos = {}
    for w, ix in (inv or {}).items():
        for i in ix:
            pos[i] = w
    return re.sub(r'\s+', ' ', ' '.join(pos[i] for i in sorted(pos))).strip()


def collect_arxiv(ids):
    out = {}
    ids = sorted(ids)
    for i in range(0, len(ids), 25):
        chunk = ids[i:i + 25]
        url = 'https://export.arxiv.org/api/query?id_list=%s&max_results=%d' % (','.join(chunk), len(chunk) + 5)
        t = fetch(url)
        if not t:
            continue
        for e in re.findall(r'<entry>(.*?)</entry>', t, re.S):
            m = re.search(r'<id>http[s]?://arxiv\.org/abs/(.*?)</id>', e)
            s = re.search(r'<summary>(.*?)</summary>', e, re.S)
            ti = re.search(r'<title>(.*?)</title>', e, re.S)
            if not m or not s:
                continue
            out[norm_arxiv(m.group(1))] = {
                'title': re.sub(r'\s+', ' ', ti.group(1)).strip() if ti else '',
                'abs': re.sub(r'\s+', ' ', s.group(1)).strip(),
            }
        time.sleep(1)
        print('  arXiv %d/%d 批，累计 %d 条' % (min(i + 25, len(ids)), len(ids), len(out)), file=sys.stderr)
    return out


def collect_openalex(dois):
    out = {}
    dois = sorted(dois)
    for i in range(0, len(dois), 20):
        chunk = dois[i:i + 20]
        f = '|'.join('https://doi.org/' + d for d in chunk)
        url = 'https://api.openalex.org/works?filter=doi:%s&per-page=%d&mailto=%s' % (f, len(chunk) + 5, MAILTO)
        t = fetch(url)
        if not t:
            continue
        try:
            j = json.loads(t)
        except Exception:
            continue
        for w in j.get('results', []):
            d = (w.get('doi') or '').replace('https://doi.org/', '').lower()
            if not d:
                continue
            out[d] = {'title': re.sub(r'\s+', ' ', (w.get('title') or '')).strip(),
                      'abs': openalex_abstract(w.get('abstract_inverted_index'))}
        time.sleep(0.6)
        print('  OpenAlex %d/%d 批，累计 %d 条' % (min(i + 20, len(dois)), len(dois), len(out)), file=sys.stderr)
    return out


def classify(stored, sources):
    """sources: {名称: 摘要文本}"""
    st = (stored or '').strip()
    if not st:
        return 'empty', '', 0, ''
    frags = [x.strip() for x in st.split(ELLIPSIS) if len(x.strip()) > 20]
    whole = sq(st.rstrip(ELLIPSIS).rstrip(' .'))
    for name, ab in sources.items():
        sab = sq(ab)
        if not sab:
            continue
        if whole and whole in sab:
            return 'consistent', name, len(ab), ab[-40:]
        if frags:
            hit = sum(1 for f in frags if sq(f) in sab)
            if hit == len(frags):
                return 'truncated_snippet', name, len(ab), ab[-40:]
            if hit:
                return 'partial', name, len(ab), ab[-40:]
    if any(sq(ab) for ab in sources.values()):
        return 'zero_hit', ';'.join(sources), 0, ''
    return 'no_identifier', '', 0, ''


def main():
    path = 'lit/bibliography.csv'
    rows = list(csv.DictReader(open(path, encoding='utf-8')))
    print('读入 %d 行' % len(rows), file=sys.stderr)

    ident = [extract(r) for r in rows]
    ax_ids = {a for a, d in ident if a}
    dois = {d for a, d in ident if d}
    print('可定位：arXiv id %d 个、DOI %d 个（去重后）' % (len(ax_ids), len(dois)), file=sys.stderr)

    print('拉取 arXiv…', file=sys.stderr)
    ax = collect_arxiv(ax_ids)
    print('拉取 OpenAlex…', file=sys.stderr)
    oa = collect_openalex(dois)

    out = []
    key_rows = {}
    for n, (r, (aid, doi)) in enumerate(zip(rows, ident), start=2):
        src = {}
        if aid and aid in ax:
            src['arxiv'] = ax[aid]['abs']
        if doi and doi in oa:
            src['openalex'] = oa[doi]['abs']
        v, name, ln, tail = classify(r.get('abstract'), src)
        out.append({'row_no': n, 'title': re.sub(r'\s+', ' ', r['title'])[:100], 'year': r.get('year', ''),
                    'verdict': v, 'authority': name, 'arxiv_id': aid, 'doi': doi,
                    'authority_abs_len': ln, 'authority_tail40': tail,
                    'stored_abs_len': len((r.get('abstract') or '').strip()),
                    'has_ellipsis': 'Y' if ELLIPSIS in (r.get('abstract') or '') else 'N'})
        for k, tag in ((aid, 'arxiv'), (doi, 'doi')):
            if k:
                key_rows.setdefault((tag, k), []).append(n)

    cols = ['row_no', 'title', 'year', 'verdict', 'authority', 'arxiv_id', 'doi',
            'authority_abs_len', 'authority_tail40', 'stored_abs_len', 'has_ellipsis']
    with open('lit/audit/full304_scan.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)

    dups = {k: v for k, v in key_rows.items() if len(v) > 1}
    dup_rows = sorted({n for v in dups.values() for n in v})
    json.dump({'标识符重复': ['%s:%s -> 行%s' % (t, k, v) for (t, k), v in sorted(dups.items())]},
              open('lit/audit/duplicate_keys.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    c = Counter(o['verdict'] for o in out)
    print('\n=== 全量 %d 行分类 ===' % len(out))
    for k in ['consistent', 'truncated_snippet', 'partial', 'zero_hit', 'no_identifier', 'empty']:
        print('  %-16s %3d' % (k, c.get(k, 0)))
    ex = Counter((o['verdict'], o['has_ellipsis']) for o in out)
    print('\n  zero_hit 且不含 … :', ex.get(('zero_hit', 'N'), 0), '| zero_hit 且含 … :', ex.get(('zero_hit', 'Y'), 0))
    print('  需 LLM/人工取证的行 = zero_hit + partial + empty + no_identifier =',
          c.get('zero_hit', 0) + c.get('partial', 0) + c.get('empty', 0) + c.get('no_identifier', 0))
    print('\n=== 同 arXiv id / 同 DOI 被录多行 ===')
    print('  重复标识符 %d 组，涉及行 %d 行' % (len(dups), len(dup_rows)))
    for (t, k), v in sorted(dups.items())[:15]:
        print('   %s:%s -> %s' % (t, k, v))
    print('\n产物：lit/audit/full304_scan.csv, lit/audit/duplicate_keys.json', file=sys.stderr)


if __name__ == '__main__':
    main()
