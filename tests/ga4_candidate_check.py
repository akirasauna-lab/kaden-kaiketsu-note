"""Simulate main assets at the official URL; intercept ALL collection traffic.

Uses Google's real gtag.js to inspect page_view generation without publishing
or sending test events into the production Analytics property.
"""
import json,mimetypes,os,shutil,subprocess,sys,tempfile
from pathlib import Path
from urllib.parse import urlsplit,parse_qs,unquote
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ID=json.loads((ROOT/'config/analytics.json').read_text())['ga4_measurement_id']
ORIGIN='https://kaden-kaiketsu.com'
with tempfile.TemporaryDirectory(prefix='kaden-ga4-candidate-') as tmp:
    root=Path(tmp)
    for folder in ('config','content','site/assets'):shutil.copytree(ROOT/folder,root/folder)
    for file in ('build.py','publication_context.py'):shutil.copy2(ROOT/file,root/file)
    code="import sys,runpy;sys.path.insert(0,sys.argv[1]);import publication_context;publication_context.detect_wrangler_command=lambda:'deploy';runpy.run_path(sys.argv[1]+'/build.py',run_name='__main__')"
    subprocess.run([sys.executable,'-c',code,str(root)],env={**os.environ,'WORKERS_CI':'1','WORKERS_CI_BRANCH':'main','WRANGLER_COMMAND':'deploy'},check=True)
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
        results=[]
        for path in ('/','/articles/daikin-heating-not-warm/'):
            context=b.new_context();events=[];loaders=[]
            def route_request(route):
                req=route.request;parts=urlsplit(req.url)
                if parts.netloc=='kaden-kaiketsu.com':
                    file=root/'site'/unquote(parts.path).lstrip('/')
                    if file.is_dir():file=file/'index.html'
                    assert file.resolve().is_relative_to((root/'site').resolve())
                    if file.is_file():route.fulfill(status=200,body=file.read_bytes(),content_type=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
                    else:route.fulfill(status=404,body='missing')
                elif parts.hostname=='www.googletagmanager.com' and parts.path.startswith('/gtag/') and req.method=='GET':
                    loaders.append(req.url);route.continue_()
                else:
                    query=parse_qs(parts.query)
                    collection=False
                    for line in (req.post_data or '').splitlines() or ['']:
                        values={**query,**parse_qs(line)}
                        if values.get('en',[''])[0]=='page_view':
                            collection=True
                            events.append({key:values.get(key,[''])[0] for key in ('tid','en','dl','dt')})
                    # A synthetic success prevents transport fallback/retries.
                    # No collection request leaves the browser interception.
                    if collection:route.fulfill(status=204,headers={'Access-Control-Allow-Origin':'*'},body='')
                    else:route.abort()
            context.route('**/*',route_request)
            page=context.new_page();page.goto(ORIGIN+path,wait_until='domcontentloaded')
            for _ in range(30):
                if events:break
                page.wait_for_timeout(500)
            page.wait_for_timeout(1000)
            assert len(events)==1,(path,events,loaders)
            assert events[0]['tid']==ID and events[0]['dl']==ORIGIN+path and events[0]['dt']==page.title(),events
            commands=page.evaluate('dataLayer.filter(x=>x[0]==="config").map(x=>Array.from(x))')
            assert commands==[['config',ID]],commands
            results.append({'path':path,'page_view':events[0],'collection_blocked':True})
            context.close()
        b.close()
print(json.dumps({'production_candidate':True,'published':False,'events_delivered_to_ga4':False,'results':results,'result':'PASS'},ensure_ascii=True))
