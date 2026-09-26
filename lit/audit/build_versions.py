#!/usr/bin/env python3
"""为 bibliography.csv 每一行构建「版本与链接」+ 权威摘要层。

输出 lit/audit/paper_versions.csv，列：
  row_no,title,arxiv_id,doi,verdict,authority,
  arxiv_abs,arxiv_pdf,published,oa_pdf,github,homepage,
  full_abs_len,full_abstract

只走确定性批量请求：arXiv id_list（含 arxiv:doi / journal_ref / comment 元数据）
与 OpenAlex 小写 DOI filter（含 primary_location / best_oa_location）。
不修改 lit/bibliography.csv。

用法：python3 lit/audit/build_versions.py
"""

import csv
import json
import re
import sys
import time
import urllib.parse

sys.path.insert(0, 'lit/audit')
from scan_abstracts import collect_arxiv, extract, fetch, norm_arxiv, sq  # noqa: E402

MAILTO = 'audit@example.org'
ELL = '…'


def openalex_bulk(dois):
    """小写 DOI 批量 -> 详细位置信息"""
    out = {}
    dois = sorted(dois)
    for i in range(0, len(dois), 20):
        chunk = dois[i:i + 20]
        f = '|'.join('https://doi.org/' + d for d in chunk)
        url = 'https://api.openalex.org/works?filter=doi:%s&per-page=%d&mailto=%s' % (
            urllib.parse.quote(f), len(chunk) + 5, MAILTO)
        t = fetch(url)
        if t:
            try:
                j = json.loads(t)
            except Exception:
                j = {}
            for w in j.get('results', []):
                d = (w.get('doi') or '').replace('https://doi.org/', '').lower()
                if not d:
                    continue
                inv = w.get('abstract_inverted_index')
                pos = {}
                for wd, ix in (inv or {}).items():
                    for k in ix:
                        pos[k] = wd
                ab = re.sub(r'\s+', ' ', ' '.join(pos[k] for k in sorted(pos))).strip()
                pl = w.get('primary_location') or {}
                bo = w.get('best_oa_location') or {}
                out[d] = {
                    'title': re.sub(r'\s+', ' ', (w.get('title') or '')).strip(),
                    'abs': ab,
                    'landing': pl.get('landing_page_url'),
                    'pdf': pl.get('pdf_url'),
                    'oa_landing': bo.get('landing_page_url'),
                    'oa_pdf': bo.get('pdf_url'),
                    'is_oa': bool(bo.get('pdf_url') or bo.get('landing_page_url')),
                    'venue': ((pl.get('source') or {}).get('display_name')) or '',
                }
        time.sleep(0.6)
        print('  OpenAlex %d/%d，累计 %d' % (min(i + 20, len(dois)), len(dois), len(out)), file=sys.stderr)
    return out


def arxiv_raw(ids):
    """保留完整 entry，以便抽 arxiv:doi / journal_ref / comment"""
    out = {}
    ids = sorted(ids)
    for i in range(0, len(ids), 25):
        chunk = ids[i:i + 25]
        url = 'https://export.arxiv.org/api/query?id_list=%s&max_results=%d' % (
            ','.join(chunk), len(chunk) + 5)
        t = fetch(url)
        if not t:
            continue
        for e in re.findall(r'<entry>(.*?)</entry>', t, re.S):
            m = re.search(r'<id>http[s]?://arxiv\.org/abs/(.*?)</id>', e)
            if not m:
                continue

            def tg(tag):
                mm = re.search(r'<%s>(.*?)</%s>' % (tag, tag), e, re.S)
                return re.sub(r'\s+', ' ', mm.group(1)).strip() if mm else ''
            links = re.findall(r'<link href="([^"]+)"[^>]*/?>', e)
            pdf = next((l for l in links if '/pdf/' in l), '')
            out[norm_arxiv(m.group(1))] = {
                'latest_id': m.group(1),
                'title': tg('title'),
                'abs': tg('summary'),
                'comment': tg('arxiv:comment'),
                'jref': tg('arxiv:journal_ref'),
                'adoi': tg('arxiv:doi'),
                'abs_url': 'https://arxiv.org/abs/' + m.group(1),
                'pdf_url': pdf,
            }
        time.sleep(1)
        print('  arXiv %d/%d，累计 %d' % (min(i + 25, len(ids)), len(ids), len(out)), file=sys.stderr)
    return out


GH = re.compile(r'https?://(?:www\.)?github\.com/[A-Za-z0-9_.\-/]+', re.I)
HOMEPAGE = re.compile(r'https?://[A-Za-z0-9_.\-/]+', re.I)
BAD_HOST = ('arxiv.org', 'doi.org', 'dx.doi.org', 'github.com', 'openalex.org',
            'semanticscholar.org', 'proceedings.mlr.press', 'jmlr.org')


def find_links(*texts):
    blob = ' '.join(t or '' for t in texts)
    gh = GH.search(blob)
    hp = ''
    for m in HOMEPAGE.finditer(blob):
        u = m.group(0).rstrip('.,;)\'"')
        host = (urllib.parse.urlparse(u).netloc or '').lower()
        if host and not any(b in host for b in BAD_HOST) and 'github.com' not in host:
            hp = u
            break
    return (gh.group(0).rstrip('.,;)') if gh else ''), hp


def main():
    rows = list(csv.DictReader(open('lit/bibliography.csv', encoding='utf-8')))
    scan = {int(r['row_no']): r for r in csv.DictReader(open('lit/audit/full304_scan.csv', encoding='utf-8'))}
    ident = [extract(r) for r in rows]
    ax_ids = {a for a, d in ident if a}
    dois = {d for a, d in ident if d}
    print('arXiv id %d / DOI %d' % (len(ax_ids), len(dois)), file=sys.stderr)
    ax = arxiv_raw(ax_ids)
    oa = openalex_bulk(dois)

    rec = []
    for n, (r, (aid, doi)) in enumerate(zip(rows, ident), start=2):
        a = ax.get(aid) if aid else None
        o = oa.get(doi) if doi else None
        authority = scan.get(n, {}).get('verdict', '')
        # 权威摘要：优先用与存量比对成功的那个源；zero_hit 时仍取权威源（正是要替换的内容）
        cand = []
        if a and a['abs']:
            cand.append(('arxiv', a['abs']))
        if o and o.get('abs'):
            cand.append(('openalex', o['abs']))
        best = ''
        bsrc = ''
        for nm, ab in cand:
            if sq(r.get('abstract') or '') and sq(r['abstract'].strip(ELL).strip()) in sq(ab):
                best, bsrc = ab, nm
                break
        if not best:
            # 未被核验为 snippet 的（含 zero_hit）取更长的那份作为权威全文
            for nm, ab in cand:
                if len(ab) > len(best):
                    best, bsrc = ab, nm
        published = ''
        if a and a.get('adoi'):
            published = 'https://doi.org/' + a['adoi']
        elif a and a.get('jref'):
            published = ''
        if not published and doi:
            published = 'https://doi.org/' + doi
        if o:
            published = o.get('landing') or (o.get('pdf') and '') or published
        oa_pdf = (o or {}).get('oa_pdf') or (a or {}).get('pdf_url') or ''
        arx = (a or {}).get('abs_url') or (('https://arxiv.org/abs/' + aid) if aid else '')
        gh, hp = find_links((a or {}).get('comment'), (a or {}).get('abs'),
                            best, (o or {}).get('landing'), (o or {}).get('oa_landing'))
        rec.append({
            'row_no': n,
            'title': re.sub(r'\s+', ' ', r['title'])[:120],
            'arxiv_id': (a or {}).get('latest_id', aid),
            'doi': doi,
            'verdict': authority,
            'abs_authority': bsrc,
            'arxiv_abs': arx,
            'published': published,
            'oa_pdf': oa_pdf,
            'github': gh,
            'homepage': hp,
            'jref': (a or {}).get('jref', ''),
            'venue': (o or {}).get('venue', ''),
            'full_abs_len': len(best),
            'stored_abs_len': len((r.get('abstract') or '').strip()),
            'full_abstract': best,
        })

    cols = ['row_no', 'title', 'arxiv_id', 'doi', 'verdict', 'abs_authority', 'arxiv_abs',
            'published', 'oa_pdf', 'github', 'homepage', 'jref', 'venue',
            'full_abs_len', 'stored_abs_len', 'full_abstract']
    with open('lit/audit/paper_versions.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rec)

    def cnt(k):
        return sum(1 for x in rec if x[k])
    print('\n=== paper_versions.csv 覆盖情况（共 %d 行）===' % len(rec))
    for k in ['arxiv_abs', 'published', 'oa_pdf', 'github', 'homepage']:
        print('  %-10s %3d' % (k, cnt(k)))
    print('  full_abstract 非空 %d；其中比存量更长 %d' % (
        sum(1 for x in rec if x['full_abstract']),
        sum(1 for x in rec if x['full_abstract'] and x['full_abs_len'] > x['stored_abs_len'])))
    print('  无任何权威摘要（需 LLM 标题反查）: %d' % sum(1 for x in rec if not x['full_abstract']))


if __name__ == '__main__':
    main()
