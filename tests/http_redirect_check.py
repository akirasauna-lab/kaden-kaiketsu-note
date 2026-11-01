"""Live production check. Expected to fail until Cloudflare HTTPS is enabled.

Uses request GET with redirect following disabled, not browser HSTS upgrades.
"""
from playwright.sync_api import sync_playwright
results=[]
with sync_playwright() as p:
    request=p.request.new_context()
    for path in ('/','/articles/daikin-heating-not-warm/','/articles/panasonic-humidifier-low-humidity/?from=seo'):
        r=request.get('http://kaden-kaiketsu.com'+path,max_redirects=0)
        expected='https://kaden-kaiketsu.com'+path
        results.append((r.status,r.headers.get('location'),expected))
        print('HTTP',r.status,'Location:',r.headers.get('location'),'Expected: 301',expected)
    request.dispose()
assert all(status==301 and location==expected for status,location,expected in results),'Cloudflare HTTP-to-HTTPS 301 is not configured correctly; see docs/seo-20261101-review.md'
