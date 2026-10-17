"""Package a disposable main-production simulation with Wrangler --dry-run."""
import os,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='kaden-production-package-') as tmp:
    root=Path(tmp)
    for folder in ('config','content','site/assets'):shutil.copytree(ROOT/folder,root/folder)
    for file in ('build.py','publication_context.py'):shutil.copy2(ROOT/file,root/file)
    # Substitution is confined to this test copy because this Windows machine
    # cannot observe the Linux Cloudflare process tree. No external deploy.
    code="import sys,runpy;sys.path.insert(0,sys.argv[1]);import publication_context;publication_context.detect_wrangler_command=lambda:'deploy';runpy.run_path(sys.argv[1]+'/build.py',run_name='__main__')"
    env={**os.environ,'WORKERS_CI':'1','WORKERS_CI_BRANCH':'main','WRANGLER_COMMAND':'deploy','WRANGLER_SEND_METRICS':'false'}
    subprocess.run([sys.executable,'-c',code,str(root)],env=env,check=True)
    report=json.loads((root/'site/.well-known/publication.json').read_text())
    assert report['indexing_enabled'] is True
    assert '<loc>https://kaden-kaiketsu.com/</loc>' in (root/'site/sitemap.xml').read_text()
    config=(ROOT/'wrangler.toml').read_text(encoding='utf-8')
    start=config.index('[build]');end=config.index('[assets]',start)
    (root/'wrangler.toml').write_text(config[:start]+config[end:],encoding='utf-8')
    subprocess.run([shutil.which('node'),str(ROOT/'node_modules/wrangler/bin/wrangler.js'),'deploy','--dry-run','--config',str(root/'wrangler.toml')],cwd=root,env=env,check=True)
print('PASS: main-production candidate packaged by Wrangler --dry-run; no external deployment.')
