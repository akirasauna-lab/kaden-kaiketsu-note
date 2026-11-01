"""Verify all preview HTML and navigation emit no Google Analytics requests."""
import json,sys
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
base=sys.argv[1].rstrip('/')
paths=['/__ga4_missing_page__/' if f.name=='404.html' else '/'+f.relative_to(ROOT/'site').as_posix().removesuffix('index.html') for f in (ROOT/'site').rglob('*.html')]
assert len(paths)==39
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
    context=b.new_context();requests=[]
    def observe(req):
        host=urlsplit(req.url).hostname or ''
        if any(host==domain or host.endswith('.'+domain) for domain in ('googletagmanager.com','google-analytics.com','analytics.google.com')) or '/g/collect' in req.url:requests.append(req.url)
    context.on('request',observe)
    page=context.new_page()
    for path in sorted(paths):
        r=page.goto(base+path,wait_until='networkidle')
        assert r.status==(404 if path=='/__ga4_missing_page__/' else 200),(path,r.status)
        assert page.locator('script[src*="googletagmanager"], script[src*="google-analytics"]').count()==0,path
        assert page.evaluate('typeof window.gtag')=='undefined',path
        assert 'noindex' in page.locator('meta[name="robots"]').get_attribute('content'),path
    assert not requests,requests
    b.close()
print(json.dumps({'preview':base,'html_pages':len(paths),'ga4_requests':len(requests),'ga4_scripts':0,'result':'PASS'}))
