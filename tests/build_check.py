"""Build regression checks; requires Python 3.11+ and requirements.txt."""
import json, os, shutil, subprocess, sys, tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set(); self.robots=''; self.h1=0; self.canonicals=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='meta' and a.get('name')=='robots': self.robots=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical': self.canonicals.append(a['href'])
        if tag in ('a','link','script','img'):
            u=a.get('href',a.get('src',''))
            if u.startswith(('/','#')): self.links.append(u)

def run(root,extra=None,ok=True):
    clean={k:v for k,v in os.environ.items() if k not in ('SITE_URL','OPERATOR_NAME','CONTACT_EMAIL','SITE_BUILD_TARGET','WRANGLER_COMMAND')}
    result=subprocess.run([sys.executable,str(root/'build.py')],env={**clean,**(extra or {})},capture_output=True,text=True)
    assert (result.returncode==0)==ok,result.stderr

def inspect(root,origin=''):
    site=root/'site'; pages={}
    for f in site.rglob('*.html'):
        p=Page();p.feed(f.read_text(encoding='utf-8'));pages[f]=p
        assert p.h1==1 and p.robots=='noindex,nofollow',f
        assert len(p.canonicals)==(1 if origin and f.name!='404.html' else 0),(f,p.canonicals)
        if p.canonicals:
            expected=origin+'/'+str(f.relative_to(site).parent).replace('\\','/').strip('.')
            if not expected.endswith('/'):expected+='/'
            assert p.canonicals==[expected],(f,p.canonicals,expected)
    for f,p in pages.items():
        for u in p.links:
            parts=urlsplit(u)
            path=site/unquote(parts.path).lstrip('/') if parts.path else f
            if path.is_dir():path=path/'index.html'
            assert path.exists(),(f,u)
            if parts.fragment:assert parts.fragment in pages[path].ids,(f,u)
    assert not (site/'sitemap.xml').exists(),'No sitemap of noindex content'
    assert (site/'robots.txt').read_text()=='User-agent: *\nDisallow: /\n'
    assert 'X-Robots-Tag: noindex, nofollow' in (site/'_headers').read_text()
    return len(pages)

with tempfile.TemporaryDirectory(prefix='kaden-build-') as temp:
    root=Path(temp)
    shutil.copytree(ROOT/'config',root/'config');shutil.copy2(ROOT/'build.py',root/'build.py');shutil.copytree(ROOT/'content',root/'content');shutil.copytree(ROOT/'site/assets',root/'site/assets')
    run(root);assert inspect(root)==24
    (root/'config/operator.json').write_text(json.dumps({'name':'Test','contact_email':'test@example.test'}),encoding='utf-8')
    env={'SITE_URL':'https://example.test','OPERATOR_NAME':'Test','CONTACT_EMAIL':'test@example.test'}
    run(root,env);inspect(root,'https://example.test')
    for url in ('https://example.test/path','https://example.test?x=1','https://example.test/#x','https://user:pass@example.test','https://example.test:bad','http://example.test','https://'):
        run(root,{**env,'SITE_URL':url},ok=False)
    # Simulate public output only in a disposable copy; no external deployment.
    import xml.etree.ElementTree as ET
    approval=root/'config/publication.json'
    approval.write_text(json.dumps({'indexing_approved':True,'production_origin':'https://example.test'}),encoding='utf-8')
    release={**env,'SITE_BUILD_TARGET':'production','WRANGLER_COMMAND':'deploy'}
    run(root,release)
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls=[e.text for e in ET.parse(root/'site/sitemap.xml').findall('.//s:loc',ns)]
    assert len(urls)==23 and len(set(urls))==23
    assert all(u.startswith('https://example.test/') and '404' not in u for u in urls)
    for f in (root/'site').rglob('*.html'):
        page=Page();page.feed(f.read_text(encoding='utf-8'))
        assert page.robots==('noindex,nofollow' if f.name=='404.html' else 'index,follow')
    assert 'X-Robots-Tag' not in (root/'site/_headers').read_text()
    assert 'Sitemap: https://example.test/sitemap.xml' in (root/'site/robots.txt').read_text()
    run(root,{**release,'CONTACT_EMAIL':''},ok=False)
    run(root,{**release,'OPERATOR_NAME':''},ok=False)
    run(root,{**release,'CONTACT_EMAIL':'other@example.test'},ok=False)
    run(root,{**release,'SITE_URL':'https://different.test'},ok=False)
    # Even with production flags and approval, preview/dev/direct builds are locked.
    for command in ('preview','dev',''):
        run(root,{**release,'WRANGLER_COMMAND':command});inspect(root,'https://example.test')
    run(root,{**release,'SITE_BUILD_TARGET':'preview'});inspect(root,'https://example.test')
    approval.write_text(json.dumps({'indexing_approved':False,'production_origin':'https://example.test'}),encoding='utf-8')
    run(root,release);inspect(root,'https://example.test')
    # A displayed but explicitly search-excluded article must stay out of sitemap.
    source=root/'content/articles.json'; current=json.loads(source.read_text(encoding='utf-8'))
    excluded=current[0]['slug'];current[0]['search_visible']=False
    source.write_text(json.dumps(current,ensure_ascii=False),encoding='utf-8')
    approval.write_text(json.dumps({'indexing_approved':True,'production_origin':'https://example.test'}),encoding='utf-8')
    run(root,release)
    assert excluded not in (root/'site/sitemap.xml').read_text()
    excluded_page=Page();excluded_page.feed((root/'site/articles'/excluded/'index.html').read_text(encoding='utf-8'))
    assert excluded_page.robots=='noindex,nofollow'
    del current[0]['search_visible'];source.write_text(json.dumps(current,ensure_ascii=False),encoding='utf-8')
    # Existing generated drafts must disappear after a rebuild, not merely from navigation.
    source=root/'content/articles.json'; data=json.loads(source.read_text(encoding='utf-8'))
    stale=data[-1]['slug'];data[-1]['review_status']='draft'
    source.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');run(root)
    assert not (root/'site/articles'/stale/'index.html').exists()
    assert stale not in (root/'site/index.html').read_text(encoding='utf-8')
    approval.write_text(json.dumps({'indexing_approved':True,'production_origin':'https://example.test'}),encoding='utf-8')
    run(root,release)
    urls=[e.text for e in ET.parse(root/'site/sitemap.xml').findall('.//s:loc',ns)]
    assert all(stale not in u for u in urls) and len(urls)==21  # article + now-empty category omitted
    assert '家電の解決ノート編集部' in (ROOT/'site/about/index.html').read_text(encoding='utf-8')

run(ROOT);count=inspect(ROOT)
print(f'PASS build: {count} HTML pages, internal paths/anchors, noindex, exact canonical origins, invalid origins rejected, preview locks, gated production sitemap/robots/headers, stale draft removal.')
