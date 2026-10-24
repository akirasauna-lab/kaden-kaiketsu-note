"""Publication safety tests; public artifacts are generated only in a temp copy."""
import json, os, shutil, subprocess, sys, tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from publication_context import command_from_argv,detect_wrangler_command,indexing_allowed
ORIGIN='https://kaden-kaiketsu.com'
CI_MAIN={'WORKERS_CI':'1','WORKERS_CI_BRANCH':'main','WRANGLER_COMMAND':'deploy'}
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=set();self.robots='';self.h1=0;self.canonicals=[]
        self.in_head=False;self.ads=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='head':self.in_head=True
        if tag=='script' and 'adsbygoogle' in a.get('src',''):
            self.ads.append((self.in_head,a))
        if a.get('id'):self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='meta' and a.get('name')=='robots':self.robots=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical':self.canonicals.append(a['href'])
        if tag in ('a','link','script','img'):
            u=a.get('href',a.get('src',''))
            if u.startswith(('/','#')):self.links.append(u)
    def handle_endtag(self,tag):
        if tag=='head':self.in_head=False

def run(root,env=None,actual=None,mock=False,ok=True):
    clean={k:v for k,v in os.environ.items() if not k.startswith(('WORKERS_CI','WRANGLER_')) and k not in ('SITE_URL','SITE_BUILD_TARGET','CONTACT_EMAIL','OPERATOR_NAME')}
    if mock:
        # Only this disposable build process substitutes the OS observation.
        code="import sys,runpy;sys.path.insert(0,sys.argv[1]);import publication_context;publication_context.detect_wrangler_command=lambda:"+repr(actual)+";runpy.run_path(sys.argv[1]+'/build.py',run_name='__main__')"
        args=[sys.executable,'-c',code,str(root)]
    else:args=[sys.executable,str(root/'build.py')]
    result=subprocess.run(args,env={**clean,**(env or {})},capture_output=True,text=True)
    assert (result.returncode==0)==ok,result.stderr

def inspect(root,public=False):
    site=root/'site';pages={}
    for f in site.rglob('*.html'):
        p=Page();p.feed(f.read_text(encoding='utf-8'));pages[f]=p
        assert len(p.ads)==(1 if public else 0),(f,p.ads)
        if public:
            in_head,attrs=p.ads[0]
            assert in_head and 'async' in attrs and attrs.get('crossorigin')=='anonymous',f
            assert attrs['src']=='https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2655344226898817',f
        expected='index,follow' if public and f.name!='404.html' else 'noindex,nofollow'
        assert p.robots==expected and p.h1==1,(f,p.robots)
        path='/'+str(f.relative_to(site).parent).replace('\\','/').strip('.')
        if not path.endswith('/'):path+='/'
        assert p.canonicals==([] if f.name=='404.html' else [ORIGIN+path]),f
    for f,p in pages.items():
        for u in p.links:
            parts=urlsplit(u);path=site/unquote(parts.path).lstrip('/') if parts.path else f
            if path.is_dir():path=path/'index.html'
            assert path.exists(),(f,u)
            if parts.fragment:assert parts.fragment in pages[path].ids,(f,u)
    headers=(site/'_headers').read_text()
    if public:
        assert (site/'ads.txt').read_text()=='google.com, pub-2655344226898817, DIRECT, f08c47fec0942fa0\n'
    else:assert not (site/'ads.txt').exists()
    if public:
        assert 'X-Robots-Tag' not in headers.split('/.well-known/publication.json')[0]
        assert (site/'robots.txt').read_text()==f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n'
        urls=[x.text for x in ET.parse(site/'sitemap.xml').findall('.//{*}loc')]
        assert len(urls)==35 and len(set(urls))==35
        assert set(urls)=={x for p in pages.values() for x in p.canonicals}
    else:
        assert not (site/'sitemap.xml').exists()
        assert (site/'robots.txt').read_text()=='User-agent: *\nDisallow: /\n'
        assert 'X-Robots-Tag: noindex, nofollow' in headers
    for slug in ('about','editorial','privacy'):
        assert 'mailto:akirasauna@gmail.com' in (site/slug/'index.html').read_text(encoding='utf-8')
    return len(pages)

node='/usr/bin/node';cli='/project/node_modules/wrangler/wrangler-dist/cli.js'
assert command_from_argv([node,cli,'deploy','--dry-run'])=='deploy'
assert command_from_argv([node,cli,'preview'])=='preview'
assert command_from_argv([node,cli,'dev'])=='dev'
assert command_from_argv([node,cli,'versions','upload'])=='versions upload'
assert command_from_argv([node,cli,'--config','x','deploy']) is None
assert command_from_argv(['/bin/sh','-c','node '+cli+' deploy']) is None
with tempfile.TemporaryDirectory(prefix='kaden-publication-') as tmp:
    root=Path(tmp)
    # Model the actual Linux /proc ancestry without relying on mutable env flags.
    proc=root/'proc'
    def process(pid,parent,argv):
        p=proc/str(pid);p.mkdir(parents=True,exist_ok=True)
        (p/'cmdline').write_bytes(b'\0'.join(x.encode() for x in argv)+b'\0')
        (p/'status').write_text(f'Name: process\nPPid:\t{parent}\n')
    process(20,30,['/bin/sh','-c','python build.py']);process(30,1,[node,cli,'preview'])
    assert detect_wrangler_command(proc,20)=='preview'
    process(30,1,[node,cli,'deploy']);assert detect_wrangler_command(proc,20)=='deploy'
    process(30,1,[node,cli,'--unknown']);assert detect_wrangler_command(proc,20) is None
    assert detect_wrangler_command(proc,999) is None
    for name in ('config','content','site/assets'):shutil.copytree(ROOT/name,root/name)
    for name in ('build.py','publication_context.py'):shutil.copy2(ROOT/name,root/name)
    run(root);assert inspect(root)==36
    for env,actual in [({},'deploy'),({'WORKERS_CI':'1'},'deploy'),({**CI_MAIN,'WORKERS_CI':'0'},'deploy'),({**CI_MAIN,'WORKERS_CI_BRANCH':'feature/test'},'deploy'),({**CI_MAIN,'WORKERS_CI_BRANCH':''},'deploy'),({**CI_MAIN,'WRANGLER_COMMAND':'dev'},'dev'),({**CI_MAIN,'WRANGLER_COMMAND':''},'deploy'),(CI_MAIN,'preview'),(CI_MAIN,'dev'),(CI_MAIN,'versions upload')]:
        run(root,env,actual,mock=True);inspect(root)
    run(root,CI_MAIN,None,mock=True,ok=False)
    run(root,CI_MAIN,'deploy',mock=True);inspect(root,public=True)
    stale={'SITE_URL':'https://wrong.test','CONTACT_EMAIL':'wrong@example.test','OPERATOR_NAME':'Wrong','SITE_BUILD_TARGET':'preview'}
    run(root,{**CI_MAIN,**stale},'deploy',mock=True);inspect(root,public=True)
    approval=root/'config/publication.json';config=json.loads(approval.read_text())
    config['indexing_approved']=False;approval.write_text(json.dumps(config))
    run(root,CI_MAIN,'deploy',mock=True);inspect(root)
    config['indexing_approved']=True;approval.write_text(json.dumps(config))
    for bad in ('https://example.test/path','https://example.test?x=1','https://user:pass@example.test','http://example.test','https://'):
        approval.write_text(json.dumps({**config,'production_origin':bad}));run(root,ok=False)
    approval.write_text(json.dumps(config))
    operator=root/'config/operator.json';saved=operator.read_text(encoding='utf-8');operator.write_text('{"name":"","contact_email":""}')
    run(root,CI_MAIN,'deploy',mock=True,ok=False);operator.write_text(saved,encoding='utf-8')
    source=root/'content/articles.json';data=json.loads(source.read_text(encoding='utf-8'));excluded=data[0]['slug'];data[0]['search_visible']=False
    source.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');run(root,CI_MAIN,'deploy',mock=True)
    assert excluded not in (root/'site/sitemap.xml').read_text()
    p=Page();p.feed((root/'site/articles'/excluded/'index.html').read_text(encoding='utf-8'));assert p.robots=='noindex,nofollow'
    del data[0]['search_visible'];stale=data[-1]['slug'];data[-1]['review_status']='draft'
    source.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');run(root,CI_MAIN,'deploy',mock=True)
    assert not (root/'site/articles'/stale/'index.html').exists()
    assert stale not in (root/'site/sitemap.xml').read_text()
run(ROOT);count=inspect(ROOT)
print(f'PASS: {count} HTML pages/links/canonical; saved config; actual Wrangler parser; main production vs preview/dev/other branches/missing metadata; sitemap/robots/headers; drafts/search exclusions.')
