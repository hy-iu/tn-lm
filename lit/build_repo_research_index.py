#!/usr/bin/env python3
"""Stage reviewed repository research notes; network and installation are explicit modes."""
import argparse, gzip, hashlib, html, json, re, shutil, subprocess, tarfile, time, zipfile
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'lit/audit/repo_research_plan.json'
class Meta(HTMLParser):
    def __init__(self):super().__init__();self.values={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta' and a.get('name','').startswith('citation_'):
            self.values.setdefault(a['name'],[]).append(a.get('content',''))
def fetch(url,out):
    result=subprocess.run(['curl','-L','--fail','--silent','--show-error','--retry','1','--retry-delay','2','--max-time','60',url,'-o',str(out)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr.strip()[-350:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unpack(archive,dest):
    dest.mkdir(parents=True,exist_ok=True)
    def safe(name):
        p=dest/name
        if not p.resolve().is_relative_to(dest.resolve()):raise ValueError('Unsafe archive path')
        return p
    if tarfile.is_tarfile(archive):
        with tarfile.open(archive) as t:
            for m in t.getmembers():
                p=safe(m.name)
                if m.isdir():p.mkdir(parents=True,exist_ok=True)
                elif m.isfile():
                    if m.size>128*1024*1024:raise ValueError('Archive member exceeds 128 MiB')
                    p.parent.mkdir(parents=True,exist_ok=True)
                    with t.extractfile(m) as src,p.open('wb') as dst:shutil.copyfileobj(src,dst)
                else:raise ValueError('Archive contains links or special files')
    elif zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            for m in z.infolist():
                p=safe(m.filename)
                if m.is_dir():p.mkdir(parents=True,exist_ok=True)
                else:
                    if (m.external_attr>>16)&0o170000==0o120000:raise ValueError('ZIP contains symlink')
                    if m.file_size>128*1024*1024:raise ValueError('Archive member exceeds 128 MiB')
                    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(m))
    else:
        data=archive.read_bytes()
        if data.startswith(b'\x1f\x8b'):data=gzip.decompress(data)
        if b'\\documentclass' not in data and b'\\begin{document}' not in data:raise ValueError('Response is not a TeX source archive')
        (dest/'main.tex').write_bytes(data)
    tex=sorted(str(p.relative_to(dest)) for p in dest.rglob('*.tex'))
    if not tex:raise ValueError('No .tex files in source archive')
    return tex

def bib(p):
    key='arxiv'+p['arxiv'].replace('.','') if p.get('arxiv') else 'paper'+hashlib.sha256(p['url'].encode()).hexdigest()[:10]
    fields={'title':p['title'],'author':' and '.join(p.get('authors',[])),'year':str(p.get('year') or ''),'url':p['url']}
    if p.get('venue'):fields['note']=p['venue']
    if p.get('arxiv'):fields.update(eprint=p['arxiv'],archivePrefix='arXiv')
    return '@misc{'+key+',\n'+''.join('  '+k+' = {'+str(v).replace('{','\\{').replace('}','\\}')+'},\n' for k,v in fields.items() if v)+'}\n'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',type=Path,default=Path('/tmp/repo-research-bundle'));ap.add_argument('--repos',type=Path,default=Path.home()/'repos');ap.add_argument('--download',action='store_true');ap.add_argument('--install',action='store_true');args=ap.parse_args()
    plan=json.loads(PLAN.read_text());stage=args.stage;stage.mkdir(parents=True,exist_ok=True)
    if args.install:
        install(stage,args.repos);return
    lib=json.loads(re.search(r'^const PAPERS=(.*);$',(ROOT/'app/library.html').read_text(),re.M)[1])
    ids=sorted(set(plan['remote_papers']+[a for r in plan['repos'].values() for a in r['arxiv']]))
    papers={};workspace=ROOT/'lit/arxiv_papers';cache=stage/'download_cache';cache.mkdir(exist_ok=True)
    for aid in ids:
        matches=[p for p in lib if re.search(r'arxiv\.org/(?:abs|pdf|html)/'+re.escape(aid)+r'(?!\d)',p['u']+' '+str(p['lk']))]
        p=matches[0] if matches else {}
        code_links = []
        for match in matches:
            for link in match.get('lk', []):
                if ('github.com' in link[1] or 'huggingface.co' in link[1]) and link not in code_links:
                    code_links.append(link)
        record={'arxiv':aid,'title':p.get('t','arXiv:'+aid),'authors':[a.strip() for a in p.get('a','').split(',') if a.strip()],'year':p.get('y'),'venue':p.get('v',''),'url':'https://arxiv.org/abs/'+aid,'code_links':code_links,'metadata_source':'现有论文库题录，可能有缩写'}
        if args.download:
            try:
                absfile=cache/(aid+'.html')
                if not absfile.exists():fetch(record['url'],absfile)
                parser=Meta();parser.feed(absfile.read_text(errors='replace'));v=parser.values
                if v.get('citation_title'):
                    record['title']=v['citation_title'][0];record['authors']=v.get('citation_author',record['authors']);date=v.get('citation_date',v.get('citation_publication_date',['']))[0]
                    record['year']=int(date[:4]) if date[:4].isdigit() else record['year'];record['metadata_source']=record['url']
                versions=re.findall(r'\[v(\d+)\]',absfile.read_text(errors='replace'));record['latest_version']='v'+max(versions,key=int) if versions else None
            except Exception as e:record['metadata_fetch_error']=str(e)
        existing=sorted([p for p in workspace.glob(aid+'*') if p.is_dir() and re.fullmatch(re.escape(aid)+r'v\d+',p.name) and list(p.rglob('*.tex'))],key=lambda p:int(p.name.split('v')[-1]),reverse=True)
        assets=stage/'root/paper_sources';assets.mkdir(parents=True,exist_ok=True)
        if existing:
            src=existing[0];target=assets/src.name
            if not target.exists():shutil.copytree(src,target,ignore=shutil.ignore_patterns('__pycache__'))
            record['source']={'status':'reused_existing','version':src.name[len(aid):],'original_path':str(src),'directory':'paper_sources/'+src.name,'tex_files':sorted(str(p.relative_to(target)) for p in target.rglob('*.tex'))}
        elif args.download:
            version=record.get('latest_version') or '';name=aid+version;archive=cache/(name+'.tar');target=assets/name
            try:
                if aid=='2405.04590' and Path('/tmp/ttlm-source.tar').exists():shutil.copy2('/tmp/ttlm-source.tar',archive)
                elif not archive.exists():fetch('https://arxiv.org/src/'+name,archive)
                tex=unpack(archive,target)
                kept=assets/(name+'.tar');shutil.copy2(archive,kept)
                record['source']={'status':'downloaded_extracted','version':version or 'version_unknown','download_url':'https://arxiv.org/src/'+name,'directory':'paper_sources/'+name,'archive':'paper_sources/'+name+'.tar','sha256':sha(kept),'tex_files':tex,'checked_on':plan['checked_on']}
            except Exception as e:record['source']={'status':'download_failed','error':str(e),'download_url':'https://arxiv.org/src/'+name}
        else:record['source']={'status':'not_downloaded'}
        papers[aid]=record
        print(aid,record['source']['status'],record['title'][:65],flush=True)
    extra=[]
    for p in plan['no_arxiv_papers']:
        extra.append({'title':p['title'],'authors':p['authors'].split(', '),'year':p['year'],'venue':p['venue'],'url':p['url'],'source':{'status':'no_arxiv_or_public_tex_located','note':p['note']}})
    snapshots=[]
    for name,review in plan['repos'].items():
        folder=args.repos/name
        if not folder.is_dir():continue
        origin=subprocess.run(['git','-C',str(folder),'remote','get-url','origin'],capture_output=True,text=True).stdout.strip()
        commit=subprocess.run(['git','-C',str(folder),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
        evidence=[]
        for rel in review['paths']:
            f=folder/rel;item={'path':rel,'exists':f.exists(),'type':'directory' if f.is_dir() else 'file'}
            if f.is_file() and f.suffix in ['.py','.jl']:
                lines=f.read_text(errors='replace').splitlines();item['symbols']=[{'line':i,'definition':line.strip()} for i,line in enumerate(lines,1) if re.match(r'^\s*(class |def |function |struct )',line)][:18]
            evidence.append(item)
        snapshot={'name':name,'origin':origin or None,'commit':commit or None,**review,'implementation_paths':evidence,'papers':[papers[a] for a in review['arxiv']]}
        if review.get('paper_url'):
            non={'title':review['paper_title'],'authors':review['authors'].split(', '),'year':review['year'],'url':review['paper_url'],'source':{'status':'arxiv_id_unconfirmed'}};snapshot['papers'].append(non);extra.append(non)
        snapshots.append(snapshot);dest=stage/'repo_notes'/name;dest.mkdir(parents=True,exist_ok=True)
        note=['# '+name+' · 论文与实现索引','','核查：'+plan['checked_on']+'；基于本地 checkout 静态阅读，未运行训练。','','- 角色：'+review['role'],'- Origin：'+(origin or '本地实验，无 origin'),'- Commit：`'+(commit or '无 Git commit')+'`','','## 模型结构与实际方案','',review['architecture'],'',review.get('notes',''),'','## 实现路径','']
        for e in evidence:
            label='已检查存在' if e['exists'] else '当前 checkout 缺失，勿按可运行入口使用'
            note.append('- ['+e['path']+']('+e['path']+') — '+label)
            for sym in e.get('symbols',[])[:5]:note.append('  - L'+str(sym['line'])+'：`'+sym['definition'].replace('`','')+'`')
        note+=['','## 对应 bibliography / arXiv / TeX','']
        if not snapshot['papers']:note+=['没有确认单一对应论文／arXiv。请参照上面的仓库角色和原 README，不补造编号。']
        for p in snapshot['papers']:
            source=p['source'];note+=['### '+p['title'],'','- 作者：'+', '.join(p.get('authors',[])),'- 年份／期刊：'+str(p.get('year') or '未确认')+'；'+p.get('venue','未确认'),'- 论文：'+p['url'],'- arXiv：'+p.get('arxiv','未确认／无已定位编号'),'- TeX 状态：'+source['status']]
            if p.get('code_links'):note+=['- 公开代码／权重：'+'；'.join('['+label+']('+url+')' for label,url in p['code_links'])]
            if source.get('directory'):note+=['- 源码目录：['+source['directory']+'](../'+source['directory']+'/)','- 源码版本：'+source['version'],'- 主 TeX 候选：'+', '.join(source.get('tex_files',[])[:8])]
            if source.get('original_path'):note+=['- 已有源码原位置：'+source['original_path']]
            if source.get('error'):note+=['- 下载失败原因：'+source['error']]
            note+=['']
        note+=['BibTeX：[papers.bib](papers.bib)；结构化信息：[paper_refs.json](paper_refs.json)。','','模型结构说明是上述代码与 README 的阅读结果；背景引用不等同于官方实现。']
        (dest/'RESEARCH_NOTES.md').write_text('\n'.join(note)+'\n');(dest/'paper_refs.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n');(dest/'papers.bib').write_text('\n'.join(bib(p) for p in snapshot['papers']))
    manifest={'checked_on':plan['checked_on'],'papers':list(papers.values())+extra,'repos':snapshots,'excluded':plan['excluded'],'remote_only':'remote_papers 对应代码未自动克隆；仅收录题录、开源链接及论文源码。'}
    (stage/'root/RESEARCH_INDEX.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(stage/'root/bibliography.bib').write_text('\n'.join(bib(p) for p in manifest['papers']))
    lines=['# 科研代码、论文与实现索引','','更新：'+plan['checked_on']+'。来源：各仓库 README／代码及 arXiv 题录；未运行模型。','','## 本地仓库','','| 仓库 | 论文 arXiv | 关系／实际方案 |','|---|---|---|']
    for r in snapshots:lines.append('| ['+r['name']+']('+r['name']+'/RESEARCH_NOTES.md) | '+', '.join(r['arxiv'])+' | '+r['role']+'；'+r['architecture']+' |')
    lines+=['','## 已核查代码链接、但尚无本地 checkout 的论文','']
    for aid in plan['remote_papers']:
        p=papers[aid]
        lines+=['- **'+p['title']+'**（arXiv:'+aid+'）：'+'；'.join('['+label+']('+url+')' for label,url in p['code_links'])+'。源码见下表；代码未自动克隆，本地实现路径未检查。']
    for p in plan['no_arxiv_papers']:lines+=['- **'+p['title']+'**：'+p['note']+' [发表页面]('+p['url']+')。']
    lines+=['','## 论文源码','','| 论文／arXiv | TeX 状态 | 本地路径 |','|---|---|---|']
    for p in manifest['papers']:
        src=p['source'];d=src.get('directory');lines.append('| ['+(p.get('arxiv') or p['title'])+']('+p['url']+') | '+src['status']+' | '+('['+d+']('+d+'/)' if d else src.get('note',src.get('error','未定位公开源码'))) .replace('|','/')+' |')
    lines+=['','下载失败保持为失败状态，不把 PDF 当作 TeX。复用的历史版本与 arXiv 最新版本分别记录，未自动替换已有源文件。','','BibTeX：[bibliography.bib](bibliography.bib)；完整元数据：[RESEARCH_INDEX.json](RESEARCH_INDEX.json)。','',*plan['excluded']]
    (stage/'root/RESEARCH_INDEX.md').write_text('\n'.join(lines)+'\n')
    # Installation plan contains only new notes and source assets, never training code.
    files=[]
    for source in (stage/'root').rglob('*'):
        if source.is_file():files.append({'from':str(source),'relative_to_repos':str(source.relative_to(stage/'root')),'sha256':sha(source)})
    for source in (stage/'repo_notes').rglob('*'):
        if source.is_file():files.append({'from':str(source),'relative_to_repos':str(source.relative_to(stage/'repo_notes')),'sha256':sha(source)})
    (stage/'install_plan.json').write_text(json.dumps({'files':files},ensure_ascii=False,indent=2)+'\n')
    (ROOT/'lit/audit/repo_research_inventory.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('STAGED',len(snapshots),'repositories;',len(papers),'arXiv papers;',len(files),'files;',stage,flush=True)

def install(stage,repos):
    plan=json.loads((stage/'install_plan.json').read_text());pending=[]
    for f in plan['files']:
        src=Path(f['from']);dst=repos/f['relative_to_repos']
        if not dst.resolve().is_relative_to(repos.resolve()):raise ValueError('Destination escaped repos')
        if sha(src)!=f['sha256']:raise ValueError('Staged file changed')
        if dst.exists() and sha(dst)!=f['sha256']:raise ValueError('Existing file differs; refusing overwrite: '+str(dst))
        pending.append((src,dst))
    for src,dst in pending:
        dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists():shutil.copy2(src,dst)
    for src,dst in pending:
        if sha(src)!=sha(dst):raise ValueError('Installed file checksum differs')
    print('Installed and verified',len(pending),'files under',repos)
if __name__=='__main__':main()
