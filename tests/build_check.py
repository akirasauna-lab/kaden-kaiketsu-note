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
    clean={k:v for k,v in os.environ.items() if k not in ('SITE_URL','OPERATOR_NAME','CONTACT_EMAIL')}
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
    shutil.copy2(ROOT/'build.py',root/'build.py');shutil.copytree(ROOT/'content',root/'content');shutil.copytree(ROOT/'site/assets',root/'site/assets')
    run(root);assert inspect(root)==24
    env={'SITE_URL':'https://example.test','OPERATOR_NAME':'Test','CONTACT_EMAIL':'test@example.test'}
    run(root,env);inspect(root,'https://example.test')
    for url in ('https://example.test/path','https://example.test?x=1','https://example.test/#x','https://user:pass@example.test','https://example.test:bad','http://example.test','https://'):
        run(root,{**env,'SITE_URL':url},ok=False)
    # Existing generated drafts must disappear after a rebuild, not merely from navigation.
    source=root/'content/articles.json'; data=json.loads(source.read_text(encoding='utf-8'))
    stale=data[-1]['slug'];data[-1]['review_status']='draft'
    source.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');run(root)
    assert not (root/'site/articles'/stale/'index.html').exists()
    assert stale not in (root/'site/index.html').read_text(encoding='utf-8')
run(ROOT);count=inspect(ROOT)
print(f'PASS build: {count} HTML pages, internal paths/anchors, noindex, exact canonical origins, invalid origins rejected, no sitemap, stale draft removal.')
