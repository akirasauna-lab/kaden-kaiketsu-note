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
    const message = document.querySelector('.check-copy-message');
    const model = document.querySelector('#consultation-model');
    const notes = document.querySelector('#consultation-notes');
    const reportOutput = document.querySelector('#consultation-report');
    const reportLabel = document.querySelector('.consultation-report-label');
    function invalidateReport() {
      if (!reportOutput || reportOutput.hidden) return;
      reportOutput.value = '';
      reportOutput.hidden = true;
      if (reportLabel) reportLabel.hidden = true;
      if (message) message.textContent = '内容が変わりました。相談用メモを再作成してください。';
    }
    for (const field of document.querySelectorAll('#consultation-model, #consultation-notes, [name="observed-case"]')) {
      field.addEventListener('input', invalidateReport);
    }
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
    boxes.forEach(b => b.addEventListener('change', () => { if(message)message.textContent='';invalidateReport();update(); }));
    guide.querySelector('.check-reset')?.addEventListener('click', () => {
      boxes.forEach(b => { b.checked = false; });
      invalidateReport();
      update();
      if(message) message.textContent = 'チェックを解除しました。';
    });
    document.querySelector('.consultation-clear')?.addEventListener('click', () => {
      if (model) model.value = '';
      if (notes) notes.value = '';
      for (const choice of document.querySelectorAll('[name="observed-case"]')) choice.checked = false;
      if (reportOutput) {
        reportOutput.value = '';
        reportOutput.hidden = true;
      }
      if (reportLabel) reportLabel.hidden = true;
      if (message) message.textContent = '相談メモを消去しました。';
    });
    document.querySelector('.check-copy')?.addEventListener('click', async () => {
      const done = boxes.map((b,i) => b.checked ? i : -1).filter(i => i >= 0);
      const selectedCase = document.querySelector('[name="observed-case"]:checked');
      const nextAction = selectedCase?.closest('.decision-case')?.querySelector('.decision-action')?.textContent;
      const report = [
        title,
        `機種・OS: ${model?.value.trim() || '未記入'}`,
        `観察した状態: ${selectedCase?.value || '未選択'}`,
        `次の確認: ${nextAction || '本文の対象範囲・公式資料を確認'}`,
        `表示・変化: ${notes?.value.trim() || '未記入'}`,
        `確認済み: ${done.length}/${boxes.length}`,
        ...boxes.map((b,i) => `${b.checked ? '済' : '未'} | ${b.closest('.step')?.querySelector('h3')?.textContent || `手順${i+1}`}`),
        '参照した公式資料:',
        ...[...document.querySelectorAll('#sources a')].map(a => `${a.textContent.trim()} ${a.href}`),
        '実機検証は未実施。チェックは操作を確認した記録であり、正常動作の保証ではありません。'
      ].join('\n');
      if (reportOutput) {
        reportOutput.value = report;
        reportOutput.hidden = false;
      }
      if (reportLabel) reportLabel.hidden = false;
      try {
        await navigator.clipboard.writeText(report);
        if(message) message.textContent = '確認結果をコピーしました。';
      } catch {
        if(message) message.textContent = '自動コピーできませんでした。表示されたメモを選択してコピーしてください。';
      }
    });
    update();
  }

})();
