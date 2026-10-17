# Cloudflare Workers 配信準備

> SEO切り替えの最新仕様は [Google検索への公開準備](search-launch-preparation.md) を参照してください。以下には以前の固定noindex仕様の記録を含みます。

このブランチはnoindexを維持した公開準備版です。mainへのマージ・本番デプロイは未実施です。以下のデプロイ手順は対象アカウントと公開内容を確認してから実行する将来用です。

## ローカル確認

Python 3.11以降、Node.js 22以降を用意してください。

```text
python -m pip install -r requirements.txt
npm ci
python tests/build_check.py
npm run check:deploy
npm run dev
```

ブラウザ検査を再現する場合：

```text
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/site_check.py
```

`SITE_TEST_URL=http://127.0.0.1:8791` などを設定すると、そのURLのWorkersローカルサーバーを使います。既定はPython HTTPサーバーです。Chromeが標準Windowsパス以外の場合は `CHROME_PATH` を指定するかPlaywrightのChromiumを使います。

## Workers Builds設定

- リポジトリのルートディレクトリを使用。
- 本番ブランチは `main`。作業ブランチのpushで既存本番が更新されないことを管理画面で確認。
- Build command: `python -m pip install -r requirements.txt`。
- Deploy command（公開承認後）: `npx wrangler deploy`。
- Node/npm依存はpackage-lock.jsonによるインストールを使用。自動インストールを無効にする場合は別途 `npm ci` が必要。
- Node.js 22以降、Python 3.11以降。Workersビルド環境はPythonもサポートするが、クラウド上の成功は未確認。
- wrangler.toml の `[build] command = "python build.py"` によりdev・deploy・dry-runで最新HTMLを再生成。
- `[assets] directory = "./site"`。ルートの旧index.htmlやZIPを配信しない。
- `not_found_handling = "404-page"`、`html_handling = "force-trailing-slash"`。

## 環境変数

`SITE_URL` は正式なHTTPS originのみ（例はドキュメント上のもの：`https://example.jp`）。サブパス・クエリ・認証情報は不可。設定する場合は `OPERATOR_NAME` と `CONTACT_EMAIL` も必要。

これらはビルド時の環境変数です。Worker実行時のvarsにだけ置いても生成済みHTMLには入りません。問い合わせ先と運営名はHTMLへ表示される公開情報です。APIトークンなどの秘密情報をここに指定しないでください。

URL未確定なら環境変数を省略したプレビューを生成します。canonicalは省略し、sitemapは生成しません。SITE_URLがあってもnoindexとDisallowを維持します。インデックス許可を環境変数だけで切り替える仕組みはありません。

## 公開承認後の確認

```text
npx wrangler login
npx wrangler whoami
npx wrangler deploy --dry-run
npx wrangler deploy
```

正しいCloudflareアカウント・Worker名を確認してから実行します。今回は実デプロイしていません。Worker名は `kaden-kaiketsu-note` で、KURACALの設定は使いません。

本番でトップ・全13記事・カテゴリ・CSS/JS・robots・404、末尾スラッシュの転送、noindex metaとX-Robots-Tag、正式canonical、運営者情報を再確認してください。検索公開に進む際のsitemap等は `prepublication-review.md` の必須対応を先に行ってください。

## 公式資料

- [Static Assets](https://developers.cloudflare.com/workers/static-assets/)
- [Custom builds](https://developers.cloudflare.com/workers/wrangler/custom-builds/)
- [HTML handling](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/)
- [Build image](https://developers.cloudflare.com/workers/ci-cd/builds/build-image/)
