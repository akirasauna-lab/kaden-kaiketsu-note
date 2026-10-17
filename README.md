# 家電の解決ノート

家電トラブルを公式情報から整理する、白・青を基調とした静的サイトです。テレビ・動画配信、洗濯機、エアコン、Wi-Fi、スマートホーム、スマホ・PCの6カテゴリ・13記事。

**現在は公開準備版です。noindexを維持し、mainへのマージや本番公開は行いません。**

## 最新の確認記録

- [確定ドメイン・連絡先と本番公開前の最終確認](docs/search-publication-release.md)

- [Google検索への公開準備・承認後の切り替え・Search Console・AdSense残件](docs/search-launch-preparation.md)

- [公開前品質確認・未確認事項](docs/prepublication-review.md)
- [Workers設定と将来の公開手順](docs/workers-publishing.md)
- [初回の戦略・10候補の選別記録](docs/content-strategy.md)（当時の未検証事項は公開前品質確認で更新）

全13記事は公式資料との照合日・適用範囲・実機未検証を表示します。公式資料の整理を実体験として書きません。AdSenseや解析タグは未導入です。

## ビルド

Python 3.11以降とNode.js 22以降を使用します。

```text
python -m pip install -r requirements.txt
npm ci
python build.py
npm run check:deploy
npm run dev
```

生成元は `content/articles.json`、配信フォルダは `site/`。`review_status: draft` は生成対象外で、前回生成した下書き記事HTMLも除去します。CSS/JSは `site/assets/` にあります。

ルートの `index.html` / `articles.json` / ZIP は旧配布物です。配信しないでください。Cloudflareはwrangler.tomlに従いsite/のみ配信します。

## 検査

```text
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/build_check.py
python tests/site_check.py
```

`SITE_TEST_URL` でWorkersローカルURLを指定可能。実施済み：23ルート×375/768/1440px、内部リンクとアンカー、全カテゴリ・検索、チェック保存とコピー、404、WorkersのURL転送とnoindexヘッダー。

## SEO・連絡先

既定はnoindexです。`config/publication.json` はユーザーの検索公開承認と正式originを設定済みですが、本番ビルド条件がそろうまで解除しません。正式URL未設定ならcanonicalを省略しsitemapを生成しません。運営者名と公開連絡先は `config/operator.json` の確定値を使用し、about/editorial/privacyへ反映します。

明示承認後、承認ファイルの正式origin・SITE_URL・実問い合わせ先・本番ビルド指定・wrangler deployがそろった場合のみ、公開対象ページのsitemapとAllowのrobotsを生成できます。preview/dev/通常ビルドは引き続きnoindex。設定詳細は最新の公開準備手順を参照してください。

収益目標はAdSense月1万円。必要PVの試算は戦略書を参照し、実測ページRPMとPVで判断します。検索流入・審査承認・収益達成を保証しません。
