(() => {
 const panel=document.createElement('div');
 panel.id='memo-reference-preview';panel.className='memo-ref-panel';panel.hidden=true;
 panel.setAttribute('role','region');panel.setAttribute('aria-label','引用预览');document.body.appendChild(panel);
 let active=null,timer;
 function close(){panel.hidden=true;if(active)active.setAttribute('aria-expanded','false');active=null;}
 function defer(){clearTimeout(timer);timer=setTimeout(()=>{if(!panel.contains(document.activeElement)&&document.activeElement!==active)close();},180);}
 function show(button,refs){
  clearTimeout(timer);if(active&&active!==button)active.setAttribute('aria-expanded','false');active=button;
  panel.replaceChildren();
  refs.forEach(ref=>{
   const item=document.createElement('div');item.className='memo-ref-item';
   const title=document.createElement('div');title.className='memo-ref-title';title.textContent=ref.title;item.appendChild(title);
   const meta=document.createElement('div');meta.className='memo-ref-meta';
   meta.textContent=[ref.authors,ref.venue,ref.year].filter(Boolean).join(' · ');
   if(meta.textContent)item.appendChild(meta);
   const links=document.createElement('div');links.className='memo-ref-links';
   ref.links.forEach(([label,url])=>{const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener';const arxiv=url.match(/arxiv\.org\/(?:abs|pdf|html)\/([^/?#]+)/i);
    a.textContent=arxiv?'arXiv:'+arxiv[1].replace(/\.pdf$/i,''):label==='GitHub'?'代码 ↗':label==='项目主页'?'主页 ↗':label+' ↗';links.appendChild(a);});
   if(ref.library){const a=document.createElement('a');a.href=ref.library;a.className='memo-ref-library';a.textContent='↙ 论文库';links.appendChild(a);}
   if(ref.id){const a=document.createElement('a');a.href='#'+ref.id;a.textContent='本页解读 ↓';a.addEventListener('click',()=>{document.getElementById(ref.id).classList.add('open');close();});links.appendChild(a);}
   item.appendChild(links);
   if(typeof localAssets==='function')localAssets(ref.links.map(x=>x[1])).forEach(asset=>{const line=document.createElement('div');line.className='memo-ref-local';line.textContent=asset.label;line.title=asset.path;item.appendChild(line);});
   panel.appendChild(item);
  });
  panel.hidden=false;button.setAttribute('aria-expanded','true');
  const rect=button.getBoundingClientRect(),width=panel.offsetWidth,height=panel.offsetHeight;
  panel.style.left=Math.max(12,Math.min(rect.left,innerWidth-width-12))+'px';
  panel.style.top=Math.max(12,rect.bottom+8+height>innerHeight?rect.top-height-8:rect.bottom+8)+'px';
 }
 function attach(node,refs){
  if(!refs.length)return;
  const button=document.createElement('button');button.type='button';button.className='memo-ref';
  button.setAttribute('aria-label','查看引用：'+refs.map(r=>r.title).join('；'));button.setAttribute('aria-controls',panel.id);button.setAttribute('aria-expanded','false');
  button.innerHTML='<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M8 12l4-4M7 8l-2 2a3.5 3.5 0 005 5l2-2M8 7l2-2a3.5 3.5 0 015 5l-2 2"/></svg>';
  button.addEventListener('pointerenter',()=>show(button,refs));button.addEventListener('pointerleave',defer);
  button.addEventListener('focus',()=>show(button,refs));button.addEventListener('blur',defer);
  button.addEventListener('click',e=>{e.stopPropagation();show(button,refs);});
  node.appendChild(button);
 }
 document.querySelectorAll('#report p,#report td,#route p,#route td,#umps p,#umps td,.chart-note,.verdict').forEach(node=>{
  const text=node.textContent.toLowerCase();
  const explicit=(node.dataset.refs||'').trim().split(/\s+/).filter(Boolean);
  const ids=[...node.querySelectorAll('a[href^="#p"]')].map(a=>a.hash.slice(1));
  // Reviewed groups are authoritative, preserving all cited papers in prose order.
  const refs=explicit.length?explicit.map(key=>MEMO_REFS.find(r=>r.key===key)).filter(Boolean):
   MEMO_REFS.filter(r=>ids.includes(r.id)||[r.title,...r.aliases].some(term=>term&&text.includes(term.toLowerCase())));
  attach(node,refs);
 });
 document.querySelectorAll('.paper').forEach(paper=>attach(paper.querySelector('.p-head'),MEMO_REFS.filter(r=>r.id===paper.id)));
 panel.addEventListener('pointerenter',()=>clearTimeout(timer));panel.addEventListener('pointerleave',defer);panel.addEventListener('focusout',defer);
 document.addEventListener('click',e=>{if(!panel.contains(e.target)&&!e.target.closest('.memo-ref'))close();});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){const button=active;close();button?.focus();close();}});
 window.addEventListener('resize',close);window.addEventListener('scroll',close,{passive:true});
})();
