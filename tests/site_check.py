"""Browser checks. Set SITE_TEST_URL to test wrangler dev instead of Python HTTP."""
import json, os, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'content/articles.json').read_text(encoding='utf-8'))
server=None;base=os.environ.get('SITE_TEST_URL','')
if not base:
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'site')))
    threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
routes=['/']+['/articles/'+a['slug']+'/' for a in DATA]+['/category/'+c+'/' for c in ('tv','washing-machine','air-conditioner','wifi','smart-home','devices')]+['/about/','/editorial/','/privacy/']
with sync_playwright() as pw:
    chrome=os.environ.get('CHROME_PATH','')
    if not chrome and Path('C:/Program Files/Google/Chrome/Application/chrome.exe').exists():chrome='C:/Program Files/Google/Chrome/Application/chrome.exe'
    browser=pw.chromium.launch(**({'executable_path':chrome} if chrome else {}),headless=True)
    context=browser.new_context(permissions=['clipboard-read','clipboard-write']);page=context.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    for width in (375,768,1440):
        page.set_viewport_size({'width':width,'height':900})
        for route in routes:
            response=page.goto(base+route);assert response.status==200,(route,response.status)
            assert page.locator('h1').count()==1
            assert page.locator('meta[name="robots"]').get_attribute('content')=='noindex,nofollow'
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,route)
            if os.environ.get('SITE_TEST_URL'):assert response.headers.get('x-robots-tag')=='noindex, nofollow'
            if '/articles/' in route:
                assert page.locator('#causes').is_visible() and page.locator('#sources a').count()>0
                assert '実機検証：未実施' in page.locator('article').inner_text()
    page.goto(base)
    assert page.locator('#article-results .guide-card').count()==13
    for cat in {a['category'] for a in DATA}:
        page.locator('[data-filter="'+cat+'"]').click()
        assert page.locator('#article-results .guide-card:visible').count()==sum(a['category']==cat for a in DATA),cat
    page.locator('[data-filter="all"]').click()
    for query,slug in [('脱水','panasonic-topload-spin-vibration'),('冷えない','daikin-aircon-not-cooling'),('Netflix','netflix-tv-freezes'),('Ｗｉｎｄｏｗｓ　１１','windows-wifi-trouble')]:
        page.locator('#site-search').fill(query)
        assert page.locator('#article-results .guide-card:visible').count()==1,query
        assert slug in page.locator('#article-results .guide-card:visible').get_attribute('href')
    page.locator('#site-search').fill('存在しない検索語');assert page.locator('#empty-state').is_visible()
    page.locator('#reset-search').click();assert page.locator('#result-count').inner_text()=='13'
    page.set_viewport_size({'width':375,'height':900});page.locator('.mobile-menu').click();assert page.locator('#mobile-nav').is_visible()
    page.locator('#mobile-nav a').first.click();assert page.locator('#mobile-nav').is_hidden()
    page.goto(base+'/articles/daikin-aircon-not-cooling/')
    page.locator('.step-check input').first.check();page.reload();assert page.locator('.step-check input').first.is_checked()
    page.locator('.check-copy').click();assert '確認済み: 1/4' in page.evaluate('navigator.clipboard.readText()')
    page.locator('.check-reset').click();assert not page.locator('.step-check input').first.is_checked()
    assert page.goto(base+'/nonexistent-quality-check/').status==404
    if os.environ.get('SITE_TEST_URL'):
        response=context.request.get(base+'/articles/daikin-aircon-not-cooling',max_redirects=0)
        assert response.status in (301,302,307,308)
        assert response.headers['location'].endswith('/articles/daikin-aircon-not-cooling/')
        response=context.request.get(base+'/sitemap.xml');assert response.status==404
        assert 'Disallow: /' in context.request.get(base+'/robots.txt').text()
    out=Path(os.environ.get('KADEN_SCREENSHOT_DIR',str(ROOT/'test-artifacts')));out.mkdir(exist_ok=True)
    for route,name in [('/','home'),('/articles/fire-tv-wifi-connect/','article-existing'),('/articles/netflix-tv-freezes/','article-new')]:
        page.goto(base+route)
        page.screenshot(path=str(out/(name+'-mobile.png')),full_page=True)
    assert not errors,errors
    browser.close()
if server:server.shutdown()
print(f'PASS browser: {len(routes)} routes x 3 widths = {len(routes)*3}; all 13 articles, all 6 filters, search/normalization, empty/reset, mobile menu, checklist/persistence/copy, 404; no JS errors. Backend: {base}')
