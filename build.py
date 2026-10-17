#!/usr/bin/env python3
"""Dependency-free (except Jinja2) static site generator for 家電の解決ノート.
Usage: pip install jinja2 && SITE_URL=https://your-domain.jp python build.py
Without SITE_URL, generated pages work locally and omit canonical and sitemap absolute URLs.
"""
import html, json, os, re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from jinja2 import Environment, BaseLoader, select_autoescape

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'site'
ALL_DATA=json.loads((ROOT/'content'/'articles.json').read_text(encoding='utf-8'))
DATA=[a for a in ALL_DATA if a.get('review_status') != 'draft']
for a in DATA:
    if a.get('review_status') == 'official-reviewed':
        for field in ('verified','scope','causes','steps','trouble','sources'):
            if not a.get(field): raise ValueError(f"Missing review field: {a['slug']} {field}")
        if a.get('hardware_tested') is not False:
            raise ValueError('Hardware claims require a separate evidence workflow')
SITE_URL=os.environ.get('SITE_URL','').rstrip('/')
CONTACT_EMAIL=os.environ.get('CONTACT_EMAIL','').strip()
OPERATOR_NAME=os.environ.get('OPERATOR_NAME','').strip()
if CONTACT_EMAIL and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', CONTACT_EMAIL):
    raise ValueError('CONTACT_EMAIL must be a valid email address')
if SITE_URL and not (OPERATOR_NAME and CONTACT_EMAIL):
    raise ValueError('Public production builds require OPERATOR_NAME and CONTACT_EMAIL')
if SITE_URL:
    origin=urlparse(SITE_URL)
    if (origin.scheme!='https' or not origin.hostname or origin.path not in ('','/')
            or origin.query or origin.fragment or origin.username or origin.password
            or any(c.isspace() for c in SITE_URL)):
        raise ValueError('SITE_URL must be an HTTPS origin without path, query or credentials')
    try: origin.port
    except ValueError: raise ValueError('SITE_URL has an invalid port')
# Remove generated article/category pages that are no longer eligible (including drafts).
for folder,allowed in [('articles',{a['slug'] for a in DATA})]:
    for stale in (OUT/folder).glob('*/index.html'):
        if stale.parent.name not in allowed:
            if not stale.resolve().is_relative_to(OUT.resolve()):
                raise ValueError('Refusing to clean outside site directory')
            stale.unlink()
            if not any(stale.parent.iterdir()): stale.parent.rmdir()
NAV=[('テレビ・動画','tv','tv'),('洗濯機','washing-machine','washer'),('エアコン','air-conditioner','aircon'),('Wi-Fi・ネット','wifi','wifi'),('スマートホーム','smart-home','smart'),('スマホ・PC','devices','laptop')]
# iPhone/Windows guides are shown in a practical separate category, without rewriting original article category
for item in DATA:
    if item['slug'] in ('iphone-wifi-unavailable','windows-wifi-trouble'):
        item['category']='スマホ・PC'
CAT_SLUG={x[0]:x[1] for x in NAV}
CAT_ICON={x[0]:x[2] for x in NAV}
ICONS={
'washer':'<rect x="4" y="2" width="16" height="20" rx="2"/><circle cx="12" cy="14" r="5"/><path d="M7 6h2m3 0h5"/>',
'aircon':'<rect x="2" y="3" width="20" height="9" rx="2"/><path d="M5 9h14M7 15v4m5-4v6m5-6v4"/>',
'logo':'<path d="M6.5 16.5c3-3.3 8-3.3 11 0"/><path d="M3 12.5c5.2-5.7 12.8-5.7 18 0"/><circle cx="12" cy="20" r="1.2" fill="currentColor" stroke="none"/>',
'tv':'<rect x="3" y="5" width="18" height="13" rx="2"/><path d="M8 22h8M12 18v4"/>',
'wifi':'<path d="M2.5 8.5a15 15 0 0 1 19 0M5.5 12a10 10 0 0 1 13 0M8.8 15.5a5 5 0 0 1 6.4 0"/><circle cx="12" cy="19" r="1" fill="currentColor" stroke="none"/>',
'smart':'<rect x="6.5" y="2.5" width="11" height="19" rx="3"/><path d="M10 6h4M11 17.5h2"/><path d="M2.5 8.5c-1 2.2-1 4.8 0 7M21.5 8.5c1 2.2 1 4.8 0 7"/>',
'laptop':'<rect x="4" y="4" width="16" height="12" rx="2"/><path d="m2 20 2-4h16l2 4H2Z"/>',
'search':'<circle cx="10.7" cy="10.7" r="6.2"/><path d="m16 16 5 5"/>',
'right':'<path d="m9 5 7 7-7 7"/>',
'arrow':'<path d="M4 12h16m-6-6 6 6-6 6"/>',
'check':'<path d="m5 12 4 4L19 6"/>',
'info':'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10h.01"/>',
'book':'<path d="M12 7c-3-2-7-2-10-1v14c4-1 7-1 10 1 3-2 6-2 10-1V6c-3-1-7-1-10 1Zm0 0v14"/>',
'light':'<path d="M9 18h6m-5 3h4m-6-5c-4-5-2.8-11 4-11s8 6 4 11c-1 1-1.5 1.5-2 2H10c-.5-.5-1-1-2-2Z"/>',
'lock':'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
'bolt':'<path d="m13 2-9 11h7l-1 9 10-12h-7l0-8Z"/>',
'chevron':'<path d="m9 18 6-6-6-6"/>',
'external':'<path d="M14 4h6v6m0-6-9 9"/><path d="M20 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h5"/>',
'menu':'<path d="M4 7h16M4 12h16M4 17h16"/>',
'clock':'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
'filter':'<path d="M4 7h16M7 12h10m-7 5h4"/>',
}
def icon(name,css=''):
    return f'<svg aria-hidden="true" class="icon {css}" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'

BASE='''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{{ page_title }}</title><meta name="description" content="{{ description }}" />
<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#ffffff"><meta property="og:locale" content="ja_JP"><meta property="og:type" content="{{ og_type }}"/><meta property="og:site_name" content="家電の解決ノート"/><meta property="og:title" content="{{ page_title }}"/><meta property="og:description" content="{{ description }}"/>
{% if canonical %}<link rel="canonical" href="{{ canonical }}"/><meta property="og:url" content="{{ canonical }}"/>{% endif %}
{% if site_url %}<meta property="og:image" content="{{ site_url }}/assets/og.svg"/>{% endif %}
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="stylesheet" href="/assets/styles.css">
{% if structured %}<script type="application/ld+json">{{ structured | safe }}</script>{% endif %}</head>
<body>
<a class="skip-link" href="#main">本文へスキップ</a>
<header class="site-header"><div class="container header-inner">
<a class="brand" href="/" aria-label="家電の解決ノート トップへ"><span class="brand-mark">{{ logo | safe }}</span><span class="brand-name">家電の解決ノート<span class="brand-en">KADEN GUIDE</span></span></a>
<nav class="header-nav" aria-label="メインメニュー"><a href="/#categories">カテゴリから探す</a><a href="/#guide-list">解決ガイド</a><a href="/about/">このサイトについて</a></nav>
<a class="header-help" href="/#search-area">{{ icon_search | safe }} <span>困りごとを探す</span></a>
<button class="mobile-menu" aria-label="メニューを開く" aria-expanded="false" aria-controls="mobile-nav">{{ icon_menu | safe }}</button>
</div><nav id="mobile-nav" class="mobile-nav" aria-label="モバイルメニュー" hidden><a href="/#categories">カテゴリから探す</a><a href="/#guide-list">解決ガイド</a><a href="/about/">このサイトについて</a></nav></header>
<main id="main">{{ content | safe }}</main>
<footer class="site-footer"><div class="container"><div class="footer-top"><div class="footer-brand"><span class="footer-brand-name">家電の解決ノート。</span><p>「動かない」を、「わかった」に。<br>毎日の家電トラブルを、ひとつずつ。</p></div><div class="footer-links"><a href="/about/">サイトについて</a><a href="/editorial/">編集方針・免責事項</a><a href="/privacy/">プライバシーポリシー</a></div></div><div class="footer-bottom"><span>© {{ year }} 家電の解決ノート</span><span>メーカー各社とは関係のない独立した情報サイトです。</span></div></div></footer>
<script src="/assets/main.js" defer></script></body></html>'''

env=Environment(loader=BaseLoader(),autoescape=select_autoescape(['html','xml']))
def render(tpl, **kwargs):return env.from_string(tpl).render(**kwargs)
def obj(data): return json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
def wrap(contents,path='/',title='',description='',og_type='website',structured=None):
    page_title = f'{title} | 家電の解決ノート' if title else '家電の解決ノート｜テレビ・洗濯機・エアコンの困りごと確認ガイド'
    return render(BASE,content=contents,page_title=page_title,description=description or 'テレビ・動画配信、洗濯機、エアコンの具体的な症状を、公式情報をもとに順番に確認するガイド。',og_type=og_type,canonical=SITE_URL+path if SITE_URL and path else '',site_url=SITE_URL,structured=obj(structured) if structured else '',logo=icon('logo'),icon_search=icon('search'),icon_menu=icon('menu'),year=date.today().year)
def output(path,text):
    loc=OUT/path
    loc.parent.mkdir(parents=True,exist_ok=True)
    loc.write_text(text,encoding='utf-8')

def category_cards():
    buff=[]
    copy={
      'テレビ・動画':('映らない、動画が固まる、リモコンが動かない',''),
      '洗濯機':('脱水時の振動、すすぎに戻る',''),
      'エアコン':('冷えない、冷たい風が出ない',''),
      'Wi-Fi・ネット':('ネットが切れる、設定が進まない','2ガイド'),
      'スマートホーム':('ハブがオフライン、家電が反応しない','3ガイド'),
      'スマホ・PC':('スマホやPCだけネットが使えない','2ガイド'),
    }
    for name, slug, ic in NAV:
        n=sum(1 for a in DATA if a['category']==name)
        caption, _ = copy[name]
        buff.append(f'<a class="category-card" href="/category/{slug}/"><span class="cat-icon">{icon(ic)}</span><span class="cat-text"><strong>{html.escape(name)}</strong><small>{html.escape(caption)}</small><span class="cat-count">{n}記事を読む {icon("arrow")}</span></span></a>')
    return ''.join(buff)

def card(a):
    return f'''<a class="guide-card" href="/articles/{a['slug']}/" data-title="{html.escape(a['title'])}" data-search="{html.escape(a['title']+' '+a['description']+' '+a['label']+' '+a['category'])}" data-cat="{html.escape(a['category'])}"><div class="card-top"><span class="card-category">{html.escape(a['category'])}</span><span class="card-min">{icon('clock')} 約{a['minutes']}分</span></div><span class="card-title">{html.escape(a['title'])}</span><span class="card-desc">{html.escape(a['description'])}</span><div class="card-bottom"><span class="brand-label">{html.escape(a['label'])}</span><span class="read-more">記事を読む {icon('arrow')}</span></div></a>'''

HERO='''<div class="hero-illustration" aria-label="接続状態の確認イメージ" role="img">
  <div class="ill-top"><span class="tiny-dot"></span><span class="tiny-dot"></span><span class="tiny-dot"></span><span class="ill-title">CONNECTION CHECK</span></div>
  <div class="ill-main"><div class="ill-center"><div class="ill-device">{{ laptop | safe }}</div><div class="ill-dash left"></div><div class="ill-status"><span class="ill-status-ring">{{ wifi | safe }}</span></div><div class="ill-dash right"></div><div class="ill-device">{{ tv | safe }}</div></div>
  <div class="ill-bubble"><span class="ill-bubble-check">{{ check | safe }}</span><span><b>つながった！</b><small>次のステップへ進めます</small></span></div>
  <div class="ill-lower"><span class="ill-lower-item"><span class="ill-online"></span> NETWORK ONLINE</span><span class="ill-lower-percent">100%</span></div>
  </div></div>'''

# Home
featured=DATA[-3:]
allcards=''.join(card(a) for a in DATA)
category_buttons='<button type="button" class="filter-chip active" data-filter="all" aria-pressed="true">すべて <span>'+str(len(DATA))+'</span></button>'
for cat,_,_ in NAV:
    category_buttons+=f'<button type="button" class="filter-chip" data-filter="{html.escape(cat)}" aria-pressed="false">{html.escape(cat)} <span>{sum(a["category"]==cat for a in DATA)}</span></button>'
home=f'''<section class="hero"><div class="container hero-grid"><div class="hero-copy"><div class="eyebrow"><span></span>家電の困りごと解決ガイド</div><h1>その家電の困りごと、<br><span>順番に確認。</span></h1><p>動画が固まる。洗濯機が脱水で揺れる。<br>エアコンが冷えない。そんなときは順番に。<br>いま試せることから、一緒に確認しましょう。</p><a class="hero-cta" href="#search-area">困りごとから探す {icon('arrow')}</a><div class="hero-foot">{icon('check')} 公式サポートを参考に、わかりやすく整理</div></div>{render(HERO,laptop=icon('laptop'),tv=icon('tv'),wifi=icon('wifi'),check=icon('check'))}</div></section>
<section class="search-section" id="search-area"><div class="container"><div class="search-panel"><div class="search-panel-label">{{search_icon}}<span>お困りごとは何ですか？</span></div><label class="search-input-wrap"><span class="sr-only">キーワード検索</span>{{search_icon}}<input type="search" id="site-search" placeholder="例：Netflix 固まる ／ 洗濯機 脱水 ／ エアコン 冷えない" autocomplete="off"/><span class="search-hint">キーワードで検索</span></label><div class="suggestion-row"><span>よくあるお悩み</span><button type="button" class="suggestion" data-query="Wi-Fi">Wi-Fiにつながらない</button><button type="button" class="suggestion" data-query="Fire TV">Fire TV</button><button type="button" class="suggestion" data-query="脱水">脱水で揺れる</button><button type="button" class="suggestion" data-query="冷えない">エアコンが冷えない</button><button type="button" class="suggestion" data-query="Netflix">動画が固まる</button></div></div></div></section>
<section class="section" id="categories"><div class="container"><div class="section-header"><div><span class="section-kicker">FIND BY CATEGORY</span><h2>使っている機器から探す</h2><p>お困りの機器・カテゴリを選んでください。</p></div></div><div class="category-grid">{category_cards()}</div></div></section>
<section class="section section-feature"><div class="container"><div class="section-header"><div><span class="section-kicker">START HERE</span><h2>まず読んでほしい解決ガイド</h2><p>テレビ・洗濯機・エアコンの症状から確認。</p></div></div><div class="featured-grid">{''.join(card(a) for a in featured)}</div></div></section>
<section class="section section-guides" id="guide-list"><div class="container"><div class="section-header"><div><span class="section-kicker">ALL GUIDES</span><h2>解決ガイド一覧</h2><p>機器や症状に合わせて、必要な記事を探せます。</p></div><span class="list-counter"><b id="result-count">{len(DATA)}</b> 件のガイド</span></div><div class="filter-row" aria-label="カテゴリで絞り込み">{category_buttons}</div><div class="guide-grid" id="article-results">{allcards}</div><div class="empty-state" id="empty-state" hidden><div>{icon('search')}</div><strong>該当する記事が見つかりませんでした</strong><p>キーワードを短くするか、カテゴリを変更してみてください。</p><button type="button" id="reset-search">絞り込みを解除する {icon('arrow')}</button></div></div></section>
<section class="section promise-section"><div class="container"><div class="promise-card"><div><span class="section-kicker">OUR PROMISE</span><h2>わからないを、<br>そのままにしない。</h2><p>メーカーの公式案内をもとに、確認すべき順番を整理。機種による違いや、安全に関わる注意点も大切にしています。</p><a href="/editorial/">編集方針を見る {icon('arrow')}</a></div><div class="promise-points"><div>{icon('check')} <span>順番どおりに確認できる</span></div><div>{icon('book')} <span>公式情報へのリンクを掲載</span></div><div>{icon('lock')} <span>危険な操作・初期化を安易に勧めない</span></div></div></div></div></section>'''
home=home.replace('{search_icon}',icon('search'))
structured={'@context':'https://schema.org','@type':'WebSite','name':'家電の解決ノート','description':'家電の設定・接続トラブルの解決ガイド'}
if SITE_URL:structured['url']=SITE_URL+'/'
output(Path('index.html'),wrap(home,structured=structured))

# Category pages
for name,slug,ic in NAV:
    subset=[a for a in DATA if a['category']==name]
    body=f'''<section class="internal-hero"><div class="container"><div class="breadcrumbs"><a href="/">トップ</a> {icon('chevron')} <span>{html.escape(name)}</span></div><span class="section-kicker">CATEGORY GUIDE</span><div class="cat-hero-title"><span class="cat-icon large">{icon(ic)}</span><div><h1>{html.escape(name)}</h1><p>「つながらない」「動かない」を、ひとつずつ確認。{len(subset)}件の解決ガイドを掲載しています。</p></div></div></div></section><section class="section"><div class="container"><div class="guide-grid">{''.join(card(a) for a in subset)}</div><p class="back-link"><a href="/#categories">{icon('arrow')} すべてのカテゴリを見る</a></p></div></section>'''
    output(Path('category')/slug/'index.html',wrap(body,f'/category/{slug}/',title=name,description=f'{name}の設定・接続・動作トラブルに関する解決ガイド一覧。'))

# Articles
for a in DATA:
    other=[x for x in DATA if x['slug']!=a['slug'] and x['category']==a['category']][:3]
    # Keep related guides relevant to the same appliance category.
    catpath=CAT_SLUG[a['category']]
    causes = ''
    if a.get('causes'):
        causes='<section class="article-section" id="causes"><h2>症状別の原因と次の確認</h2>'+''.join('<h3>'+html.escape(t)+'</h3><p>'+html.escape(d)+'</p>' for t,d in a['causes'])+'</section>'
    review = '<p class="article-note">公式資料照合：'+html.escape(a['verified'])+'。実機検証：未実施。対象・確認の限界：'+html.escape(a['scope'])+' '+html.escape(a.get('review_note',''))+'</p>'
    related = (f'''<section class="section related-section"><div class="container"><div class="section-header"><div><span class="section-kicker">RELATED GUIDES</span><h2>こちらの記事もおすすめ</h2></div></div><div class="featured-grid">{''.join(card(x) for x in other[:3])}</div></div></section>''') if other else ''
    body=f'''<div class="article-shell"><div class="container"><div class="breadcrumbs"><a href="/">トップ</a>{icon('chevron')}<a href="/category/{catpath}/">{html.escape(a['category'])}</a>{icon('chevron')}<span>解決ガイド</span></div><div class="article-layout"><article class="article-main"><header class="article-header"><div class="article-tags"><span>{html.escape(a['category'])}</span><span>{html.escape(a['label'])}</span></div><h1>{html.escape(a['title'])}</h1><p class="article-lead">{html.escape(a['lead'])}</p><div class="article-meta">{icon('clock')} 読了目安 約{a['minutes']}分 <span class="meta-separator">·</span> 記事更新：{html.escape(a["modified"])}</div></header><section class="answer-box"><div class="answer-head">{icon('check')} 結論：まず、ここから確認</div><ul>{''.join('<li>'+html.escape(x)+'</li>' for x in a['quick'])}</ul></section>{review}<div class="article-toc"><strong>この記事の内容</strong><a href="#causes">{icon('chevron')} 症状別の原因</a><a href="#steps">{icon('chevron')} まず試したい手順</a><a href="#attention">{icon('chevron')} 改善しない場合</a><a href="#faq">{icon('chevron')} よくある質問</a><a href="#sources">{icon('chevron')} 公式サポート・出典</a></div>{causes}<section class="article-section" id="steps"><span class="article-section-label">STEP BY STEP</span><h2>まず試したい手順</h2><p class="section-intro">設定を大きく変える前に、簡単に試せる項目から順に見ていきましょう。確認した項目にチェックを付けると、進捗を記録できます。</p><div class="check-progress" data-guide="{a['slug']}" data-guide-title="{html.escape(a['title'])}"><div class="check-progress-heading"><strong>確認の進み具合</strong><span class="check-progress-label" aria-live="polite">0 / {len(a['steps'])} 件確認</span></div><progress max="{len(a['steps'])}" value="0" aria-label="確認の進捗"></progress><p>チェックした内容は、この端末のブラウザにだけ保存されます。</p><div class="check-progress-actions"><button type="button" class="check-copy">確認した項目をコピー</button><button type="button" class="check-reset">チェックをリセット</button></div><span class="check-copy-message" role="status" aria-live="polite"></span></div>{''.join(f'<div class="step"><div class="step-num">{i:02d}</div><div class="step-body"><h3>{html.escape(t)}</h3><p>{html.escape(desc)}</p><label class="step-check"><input type="checkbox" data-step="{i-1}"/><span>この手順を確認した</span></label></div></div>' for i,(t,desc) in enumerate(a['steps'],1))}</section><section class="article-section" id="attention"><span class="article-section-label">IF IT STILL DOESN’T WORK</span><h2>それでも改善しない場合</h2><div class="notice">{icon('info')} <p>{html.escape(a['trouble'])}</p></div><p>機種やOSのバージョンによって画面や操作手順が異なります。解決しない場合は、メーカーの公式サポートで型番に合う案内を確認してください。</p></section><section class="article-section" id="faq"><span class="article-section-label">FAQ</span><h2>よくある質問</h2><div class="faq-list">{''.join('<details class="faq-item"><summary>'+html.escape(q)+icon('chevron')+'</summary><p>'+html.escape(ans)+'</p></details>' for q,ans in a['faq'])}</div></section><section class="article-section" id="sources"><span class="article-section-label">REFERENCE</span><h2>公式サポート・参考資料</h2><p>記事内容を確認する際に参照したメーカー公式情報です。仕様変更により内容が異なる場合は公式情報を優先してください。</p><ul class="source-links">{''.join('<li><a href="'+html.escape(url)+'" target="_blank" rel="noopener noreferrer">'+html.escape(name)+icon('external')+'</a></li>' for name,url in a['sources'])}</ul></section><div class="article-note">このページはメーカー各社の公式サポート等を参考に編集した一般的な確認ガイドです。掲載機種での実機検証を行ったことを示すものではありません。</div></article><aside class="article-sidebar"><div class="sidebar-card"><span class="sidebar-heading">この記事のポイント</span><ul>{''.join('<li>'+icon('check')+html.escape(x)+'</li>' for x in a['quick'])}</ul></div><div class="sidebar-help"><span>他の困りごとも探す</span><p>症状や機器名からガイドを検索できます。</p><a href="/#search-area">記事を検索 {icon('arrow')}</a></div></aside></div></div></div>{related}'''
    structured={'@context':'https://schema.org','@type':'Article','headline':a['title'],'description':a['description'],'inLanguage':'ja','dateModified':a['modified'],'publisher':{'@type':'Organization','name':'家電の解決ノート'}}
    if SITE_URL:structured['mainEntityOfPage']=SITE_URL+f'/articles/{a["slug"]}/'
    output(Path('articles')/a['slug']/'index.html',wrap(body,f'/articles/{a["slug"]}/',title=a['title'],description=a['description'],og_type='article',structured=structured))

# Simple editorial pages
STATIC={
'about':('このサイトについて','家電の解決ノートは、家電の接続・設定・操作で困ったときに、確認する順番を整理した独立系の情報サイトです。', '''<h2>このサイトが目指すこと</h2><p>家電の説明書や公式ヘルプは情報が充実しています。一方で、困っているときには「最初に何から調べればいいか」がわからないこともあります。そこで私たちは、疑う原因を整理し、簡単に確認できることから順番に試せる記事をまとめています。</p><h2>取り扱うテーマ</h2><p>テレビ・動画配信機器、洗濯機、エアコン、Wi-Fi・ネット接続、スマートホーム、スマホ・パソコンなどを中心に扱います。記事ごとにメーカー公式の参照先を掲載します。</p><h2>独立した情報サイトです</h2><p>メーカー各社との提携や公式サポート窓口を示すものではありません。メーカー名や商品名は識別のために記載しています。</p><h2>運営者情報</h2><p>現在は公開準備版です。公開前に運営者名・連絡方法を確定して掲載します。</p>'''),
'editorial':('編集方針・免責事項','家電の解決ノートの編集方針、出典の取り扱い、注意事項について。', '''<h2>情報の確認方法</h2><p>記事はメーカーの公式サポートページや製品情報を優先して参照し、出典リンクを各記事に記載しています。すべての製品を実機検証したものではありません。確認できない事実を使用体験として表現しない方針です。</p><h2>安全性について</h2><p>分解、配線工事、高所での作業、発熱や異臭のある機器の継続使用を推奨しません。危険があるときは直ちに使用を中止し、メーカーや資格を持つ専門業者に相談してください。</p><h2>情報の更新</h2><p>機種・アプリ・OS・公式サポートの案内は変更されることがあります。掲載時点と異なる可能性があるため、最新情報は公式資料でご確認ください。</p><h2>免責事項</h2><p>掲載内容は一般的な参考情報であり、あらゆる機器・状況での効果を保証するものではありません。設定変更による影響を確認したうえで、ご自身の判断で操作してください。</p><h2>広告について</h2><p>将来的にディスプレイ広告を掲載する予定です。広告を掲載する場合は広告と記事を区別し、読者に誤認を与えない配置を採用します。</p>'''),
'privacy':('プライバシーポリシー','家電の解決ノートのプライバシーポリシー。', '''<h2>取得する情報について</h2><p>この公開準備版のサイト自体は、会員登録や問い合わせフォームを設置しておらず、サイトの検索欄に入力した文字列を当サイトのサーバーへ送信する仕組みはありません。検索はブラウザ内で行われます。</p><h2>アクセス解析・広告配信</h2><p>現在の配布版には、Google AnalyticsやGoogle AdSenseの計測・広告タグは組み込まれていません。公開後に導入する場合は、利用するサービス、Cookie等の取扱い、オプトアウト方法などを追記して本ページを更新します。</p><h2>ブラウザへの保存</h2><p>記事のチェック機能は、お使いのブラウザのローカルストレージに確認状態を保存します。確認情報は当サイトのサーバーに送信されません。ブラウザのサイトデータを削除すると記録も削除されます。</p><h2>外部リンク</h2><p>メーカー公式サポートなどの外部サイトへのリンクがあります。移動先サイトには移動先のプライバシーポリシーが適用されます。</p><h2>ポリシーの更新</h2><p>機能・利用サービスの変更に合わせて本ポリシーを改定することがあります。</p><h2>お問い合わせ先</h2><p>公開前に連絡先を設定し、ここに掲載します。</p>''')
}
# Operator and contact are provided at launch, never invented for a preview.
if CONTACT_EMAIL and OPERATOR_NAME:
    contact_html=f'<a href="mailto:{html.escape(CONTACT_EMAIL, quote=True)}">{html.escape(CONTACT_EMAIL)}</a>'
    STATIC['about']=(STATIC['about'][0],STATIC['about'][1],STATIC['about'][2].replace('現在は公開準備版です。公開前に運営者名・連絡方法を確定して掲載します。',f'運営：{html.escape(OPERATOR_NAME)}。お問い合わせ：{contact_html}'))
    STATIC['privacy']=(STATIC['privacy'][0],STATIC['privacy'][1],STATIC['privacy'][2].replace('公開前に連絡先を設定し、ここに掲載します。',f'お問い合わせ：{contact_html}'))
for slug,(title,description,bodytext) in STATIC.items():
    body=f'<section class="internal-hero"><div class="container"><div class="breadcrumbs"><a href="/">トップ</a>{icon("chevron")}<span>{html.escape(title)}</span></div><span class="section-kicker">INFORMATION</span><h1>{html.escape(title)}</h1><p>{html.escape(description)}</p></div></section><section class="section"><div class="container"><div class="legal-body">{bodytext}</div></div></section>'
    output(Path(slug)/'index.html',wrap(body,'/'+slug+'/',title,description))
output(Path('404.html'),wrap('<section class="internal-hero"><div class="container"><span class="section-kicker">404 NOT FOUND</span><h1>ページが見つかりませんでした。</h1><p>記事のURLが変わった可能性があります。トップページから探してみてください。</p><p><a class="hero-cta" href="/">トップページへ '+icon('arrow')+'</a></p></div></section>',path=None,title='ページが見つかりません'))

# Indexing remains disabled until a separate editorial/publication decision.
(OUT/'sitemap.xml').unlink(missing_ok=True)
output(Path('robots.txt'), 'User-agent: *\nDisallow: /\n')
output(Path('_headers'), '/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
print(f'Generated {len(DATA)} articles, {len(NAV)} categories and 3 policy pages under {OUT}')
