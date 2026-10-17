"""Read-only deployed SEO check: python tests/live_seo_check.py URL production|preview.

Uses a browser network context; a Googlebot user agent does not prove access
from Google's real crawler IPs. Requires requirements-dev.txt and Chrome.
"""
import json, os, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
ORIGIN=json.loads((ROOT/'config/publication.json').read_text())['production_origin']
base=sys.argv[1].rstrip('/')
mode=sys.argv[2]
assert mode in ('production','preview')
public=mode=='production'
articles=json.loads((ROOT/'content/articles.json').read_text(encoding='utf-8'))
paths=['/']+['/articles/'+a['slug']+'/' for a in articles if a.get('review_status')!='draft']
assert len(paths)==14, 'Expected home and 13 articles'

class SEO(HTMLParser):
    def __init__(self):
        super().__init__();self.robots=[];self.canonical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta' and a.get('name','').lower() in ('robots','googlebot'):
            self.robots.append(a.get('content','').lower())
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROME_PATH','C:/Program Files/Google/Chrome/Application/chrome.exe'),headless=True)
    context=browser.new_context()
    page=context.new_page();page.goto(base+'/',wait_until='domcontentloaded')
    robots=context.request.get(base+'/robots.txt')
    assert robots.status==200 and 'text/plain' in robots.headers.get('content-type','')
    policy=RobotFileParser();policy.parse(robots.text().splitlines())
    for agent in ('Googlebot','Google-InspectionTool','*'):
        assert all(policy.can_fetch(agent,base+path)==public for path in paths), agent
    sitemap=context.request.get(base+'/sitemap.xml')
    urls=[]
    if public:
        assert sitemap.status==200
        urls=[x.text for x in ET.fromstring(sitemap.text()).findall('.//{*}loc')]
        assert len(urls)==23 and len(set(urls))==23
        assert all(u.startswith(ORIGIN+'/') for u in urls)
        assert set(ORIGIN+path for path in paths)<=set(urls)
        assert policy.site_maps()==[ORIGIN+'/sitemap.xml']
    else:assert sitemap.status==404
    for path in paths:
        r=context.request.get(base+path)
        assert r.status==200,(path,r.status)
        seo=SEO();seo.feed(r.text())
        assert seo.canonical==[ORIGIN+path],(path,seo.canonical)
        assert seo.robots and all(('noindex' not in m and 'none' not in m) if public else 'noindex' in m for m in seo.robots),(path,seo.robots)
        header=r.headers.get('x-robots-tag','').lower()
        assert ('noindex' not in header and 'none' not in header) if public else 'noindex' in header,(path,header)
    for url in urls:
        r=context.request.get(base+url.removeprefix(ORIGIN))
        assert r.status==200,(url,r.status)
        seo=SEO();seo.feed(r.text())
        assert seo.canonical==[url] and all('noindex' not in m for m in seo.robots),url
        assert 'noindex' not in r.headers.get('x-robots-tag','').lower(),url
    print(json.dumps({'url':base,'mode':mode,'home_and_articles':len(paths),'sitemap_urls':len(urls),'robots':robots.text(),'robots_cache_control':robots.headers.get('cache-control'),'result':'PASS'},ensure_ascii=False))
    browser.close()
