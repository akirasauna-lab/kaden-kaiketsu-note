"""Regression check for observation branches and private support notes."""
import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
articles = json.loads((ROOT / 'content/articles.json').read_text(encoding='utf-8'))
base = os.environ.get('SITE_TEST_URL')
server = None
if not base:
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT / 'site')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe', headless=True)
    context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'], viewport={'width': 375, 'height': 900})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    for article in articles:
        page.goto(base + '/articles/' + article['slug'] + '/', wait_until='networkidle')
        assert page.locator('.decision-case').count() == len(article['decisions']) == 2
        assert article['support_note'] in page.locator('.consultation-fields').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), article['slug']
        page.locator('[name="observed-case"]').first.check()
        page.locator('#consultation-model').fill('テスト型番 <script>')
        page.locator('#consultation-notes').fill('表示を記録。まだ再起動はしていない。')
        page.locator('.check-copy').click()
        page.wait_for_function("document.querySelector('.check-copy-message').textContent.includes('コピーしました')")
        report = page.locator('#consultation-report').input_value()
        assert report == page.evaluate('navigator.clipboard.readText()').replace('\r\n', '\n')
        assert article['decisions'][0][0] in report and article['decisions'][0][1] in report
        assert 'テスト型番 <script>' in report and '表示を記録' in report
        assert '未 | ' in report and all(url in report for _, url in article['sources'])
        assert page.locator('script:not([src])').count() == 1  # Article JSON-LD only on preview.
        page.locator('#consultation-notes').fill('変更後の記録')
        assert page.locator('#consultation-report').is_hidden()
        page.locator('.check-copy').click()
        page.locator('.consultation-clear').click()
        assert page.locator('#consultation-model').input_value() == ''
        assert page.locator('#consultation-notes').input_value() == ''
        assert page.locator('[name="observed-case"]:checked').count() == 0
        assert page.locator('#consultation-report').input_value() == ''
    # Refused clipboard permission still leaves a usable, selectable report.
    page.evaluate("Object.defineProperty(navigator.clipboard, 'writeText', {value: async () => {throw new Error('denied')}})")
    requests = []
    page.on('request', lambda request: requests.append(request.url))
    page.locator('#consultation-notes').fill('外へ送信しないテストメモ')
    page.locator('.check-copy').click()
    page.wait_for_function("document.querySelector('.check-copy-message').textContent.includes('自動コピーできませんでした')")
    assert '外へ送信しないテストメモ' in page.locator('#consultation-report').input_value()
    assert not requests, requests
    page.reload(wait_until='networkidle')
    assert page.locator('#consultation-notes').input_value() == ''
    assert page.locator('[name="observed-case"]:checked').count() == 0
    assert not errors, errors
    no_js = browser.new_context(java_script_enabled=False, viewport={'width': 375, 'height': 900})
    static = no_js.new_page()
    static.goto(base + '/articles/humidifier-water-leak/')
    assert static.locator('.decision-action').count() == 2
    assert static.locator('.decision-action').first.is_visible()
    browser.close()
if server:
    server.shutdown()
print('PASS: 26 observation guides, 375px, report/copy/clear, stale report invalidation, clipboard fallback, no submission/persistence, no-JS guidance.')

