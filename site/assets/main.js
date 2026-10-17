(() => {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const search = $('#site-search');
  const cards = [...document.querySelectorAll('#article-results .guide-card')];
  const chips = [...document.querySelectorAll('.filter-chip')];
  const count = $('#result-count');
  const empty = $('#empty-state');
  let selected = 'all';
  const normalize = (s) => (s || '').normalize('NFKC').toLocaleLowerCase('ja-JP').replace(/\s+/g, ' ').trim();
  function apply() {
    if (!search || !cards.length) return;
    const terms = normalize(search.value).split(' ').filter(Boolean);
    let found = 0;
    for (const card of cards) {
      const body = normalize(card.dataset.search);
      const ok = (selected === 'all' || card.dataset.cat === selected) && terms.every(t => body.includes(t));
      card.hidden = !ok;
      if (ok) found++;
    }
    if (count) count.textContent = String(found);
    if (empty) empty.hidden = found !== 0;
  }
  if (search) search.addEventListener('input', apply);
  for (const chip of chips) chip.addEventListener('click', () => {
    selected = chip.dataset.filter;
    for (const x of chips) { const on = x === chip; x.classList.toggle('active', on); x.setAttribute('aria-pressed', String(on)); }
    apply();
  });
  for (const btn of document.querySelectorAll('[data-query]')) btn.addEventListener('click', () => {
    if (!search) return;
    search.value = btn.dataset.query;
    selected = 'all';
    for (const x of chips) {const on = x.dataset.filter === 'all'; x.classList.toggle('active', on); x.setAttribute('aria-pressed', String(on));}
    apply();
    $('#guide-list')?.scrollIntoView({behavior:'smooth',block:'start'});
  });
  $('#reset-search')?.addEventListener('click', () => {
    if (search) search.value = '';
    selected = 'all';
    for (const x of chips) {const on = x.dataset.filter === 'all'; x.classList.toggle('active', on); x.setAttribute('aria-pressed', String(on));}
    apply();
    search?.focus();
  });
  const menu = $('.mobile-menu');
  const nav = $('#mobile-nav');
  if(menu && nav) {
    menu.addEventListener('click',()=> { const expanded=menu.getAttribute('aria-expanded')==='true';menu.setAttribute('aria-expanded',String(!expanded));menu.setAttribute('aria-label',expanded?'メニューを開く':'メニューを閉じる');nav.hidden=expanded; });
    for (const a of nav.querySelectorAll('a')) a.addEventListener('click',()=> {nav.hidden=true;menu.setAttribute('aria-expanded','false');});
  }
  // Store step-completion state only in the reader's browser; no network calls.
  const guide = document.querySelector('[data-guide]');
  if (guide) {
    const slug = guide.dataset.guide;
    const title = guide.dataset.guideTitle;
    const boxes = [...document.querySelectorAll('.step-check input[type="checkbox"]')];
    const progress = guide.querySelector('progress');
    const label = guide.querySelector('.check-progress-label');
    const message = guide.querySelector('.check-copy-message');
    const key = 'kaden-guide-check-v1:' + slug;
    const read = () => {
      try { return JSON.parse(localStorage.getItem(key) || '[]'); }
      catch { return []; }
    };
    const saved = read();
    boxes.forEach((box, i) => { box.checked = Array.isArray(saved) && saved.includes(i); });
    function update() {
      const done = boxes.map((b,i) => b.checked ? i : -1).filter(i => i >= 0);
      if (progress) progress.value = done.length;
      if (label) label.textContent = `${done.length} / ${boxes.length} 件確認`;
      boxes.forEach(b => b.closest('.step')?.classList.toggle('is-checked',b.checked));
      try { localStorage.setItem(key, JSON.stringify(done)); } catch {}
    }
    boxes.forEach(b => b.addEventListener('change', () => { if(message)message.textContent='';update(); }));
    guide.querySelector('.check-reset')?.addEventListener('click', () => {
      boxes.forEach(b => { b.checked = false; });
      update();
      if(message) message.textContent = 'チェックを解除しました。';
    });
    guide.querySelector('.check-copy')?.addEventListener('click', async () => {
      const done = boxes.map((b,i) => b.checked ? i : -1).filter(i => i >= 0);
      const report = [title,`確認済み: ${done.length}/${boxes.length}`,...boxes.map((b,i) => `${b.checked ? '済' : '未'} | ${b.closest('.step')?.querySelector('h3')?.textContent || `手順${i+1}`}`)].join('\n');
      try {
        await navigator.clipboard.writeText(report);
        if(message) message.textContent = '確認結果をコピーしました。';
      } catch {
        if(message) message.textContent = 'コピーできませんでした。ブラウザの権限設定をご確認ください。';
      }
    });
    update();
  }

})();
