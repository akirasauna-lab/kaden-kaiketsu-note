"""Read-only deployed verification: URL production|preview.

Checks every generated HTML including 404; never loads ads on production to
avoid generating test ad impressions. Preview is navigated to check requests.
"""
import json,sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
base=sys.argv[1].rstrip('/');mode=sys.argv[2]
assert mode in ('production','preview')
public=mode=='production'
SRC='https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2655344226898817'
TXT='google.com, pub-2655344226898817, DIRECT, f08c47fec0942fa0\n'
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.head=False;self.ads=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='head':self.head=True
        if tag=='script' and ('googlesyndication.com' in a.get('src','') or 'adsbygoogle' in a.get('src','')):
            self.ads.append((self.head,a))
    def handle_endtag(self,tag):
        if tag=='head':self.head=False
paths=[]
for f in (ROOT/'site').rglob('*.html'):
    path='/'+f.relative_to(ROOT/'site').as_posix()
    # Workers may serve a direct /404.html asset with 200. Inspect the same
    # template as an actual missing-route response instead.
    paths.append('/__adsense_missing_page__/' if f.name=='404.html' else path.removesuffix('index.html'))
assert len(paths)==36
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
    context=b.new_context();requests=[]
    if not public:
        context.on('request',lambda r: requests.append(r.url) if urlsplit(r.url).hostname in ('pagead2.googlesyndication.com','googleads.g.doubleclick.net') else None)
        page=context.new_page()
    for path in sorted(paths):
        r=context.request.get(base+path)
        assert r.status==(404 if path=='/__adsense_missing_page__/' else 200),(path,r.status)
        parsed=Page();parsed.feed(r.text())
        assert len(parsed.ads)==int(public),(path,parsed.ads)
        if public:
            head,a=parsed.ads[0]
            assert head and a.get('src')==SRC and a.get('crossorigin')=='anonymous' and 'async' in a,path
        else:
            page.goto(base+path,wait_until='networkidle')
            assert page.locator('script[src*="adsbygoogle"]').count()==0,path
    ads=context.request.get(base+'/ads.txt')
    if public:
        assert ads.status==200 and ads.text()==TXT
        assert 'text/plain' in ads.headers.get('content-type','')
    else:assert ads.status==404
    assert not requests,requests
    print(json.dumps({'url':base,'mode':mode,'html_pages':len(paths),'scripts_per_page':int(public),'ads_txt_status':ads.status,'preview_ad_requests':len(requests) if not public else 'not applicable','result':'PASS'}))
    b.close()
