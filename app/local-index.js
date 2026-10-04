// Match only explicit GitHub origins and arXiv identifiers, never fuzzy titles.
function localAssets(urls) {
 const found = new Map();
 for (const url of urls) {
  const gh = String(url).match(/github\.com[/:]([^/]+\/[^/#?\s]+)/i);
  const ax = String(url).match(/arxiv\.org\/(?:abs|pdf)\/(\d{4}\.\d{4,5})(?!\d)/i);
  const assets = gh ? (LOCAL_INDEX.repos[gh[1].replace(/\.git$/i, '').toLowerCase()] || []) : ax ? (LOCAL_INDEX.papers[ax[1]] || []) : [];
  assets.forEach(asset => found.set(asset.path, asset));
 }
 return [...found.values()];
}
function appendLocalAssets(container, urls) {
 const assets = localAssets(urls);
 if (!assets.length) return;
 const local = location.protocol === 'file:' || ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
 let list = container.querySelector(':scope > .local-assets');
 if (!list) {
  list = document.createElement('span');
  list.className = 'local-assets';
  container.appendChild(list);
 }
 for (const asset of assets) {
  if ([...list.children].some(row => row.dataset.path === asset.path)) continue;
  const group = document.createElement('span');
  group.className = 'local-asset';
  group.dataset.path = asset.path;
  const label = document.createElement('span');
  label.className = 'local-asset-label';
  label.textContent = asset.label.replace(/ · \d{4}\.\d{4,5}.*$/, '');
  label.title = asset.path;
  group.appendChild(label);
  // HTTP pages cannot open file: directories. Copy the path for those assets.
  if (local && (location.protocol === 'file:' || !asset.href.startsWith('file:'))) {
   const link = document.createElement('a');
   link.href = asset.href; link.textContent = '打开'; link.target = '_blank'; link.rel = 'noopener';
   group.appendChild(link);
  }
  const copy = document.createElement('button');
  copy.type = 'button'; copy.textContent = '复制路径';
  copy.addEventListener('click', async event => {
   event.stopPropagation();
   try { await navigator.clipboard.writeText(asset.path); copy.textContent = '已复制'; }
   catch { window.prompt('本地路径', asset.path); }
  });
  group.appendChild(copy); list.appendChild(group);
 }
}
// The toolbox's paper-to-code cross-reference tables are static HTML.
document.addEventListener('DOMContentLoaded', () => {
 const seen = new WeakMap();
 document.querySelectorAll('td a[href], .entry a[href]').forEach(anchor => {
  if (anchor.closest('.grow, .flat')) return;
  const container = anchor.closest('td, .entry');
  const assets = localAssets([anchor.href]);
  const paths = seen.get(container) || new Set();
  const fresh = assets.filter(asset => !paths.has(asset.path));
  if (!fresh.length) return;
  appendLocalAssets(container, [anchor.href]);
  assets.forEach(asset => paths.add(asset.path));
  seen.set(container, paths);
 });
});
