# AdSenseサイト確認コード（2026-10-24）

目的はサイト確認・審査準備のみです。広告ユニット、広告位置、CSS、記事、SEO設定は変更しません。

## 本番・プレビュー

既存の本番公開判定（承認済み・Cloudflare Workers Builds main・実際のWrangler deploy）を再利用します。確認できた本番でのみ、共通headテンプレートに次のコードを1回生成します。404.htmlを含む全36 HTMLが対象です。404のnoindexは維持します。

```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2655344226898817" crossorigin="anonymous"></script>
```

本番ビルドで配信ディレクトリsite/にads.txtを生成し、公開URL `/ads.txt` で配信します。

```text
google.com, pub-2655344226898817, DIRECT, f08c47fec0942fa0
```

プレビュー・開発・他ブランチはscriptなし、ads.txtも削除します。本番ビルド後にプレビューを作る場合も残骸を除去します。ローカルの生成物はプレビュー用なので、チェックイン済みHTMLにコードやads.txtがなくても正常です。新しい環境変数の追加は不要です。

robots.txt、sitemap、canonical、noindex、HTTPヘッダーの判定は変更しません。既存のプライバシーポリシーの「AdSense未設置」という記載のみ導入に合わせて更新し、GoogleのCookie説明と広告設定へのリンクを掲載します。

## 検査

- `python tests/build_check.py`：本番全36 HTMLにhead内1回、正しいpublisher/async/crossorigin、preview/dev/他ブランチ0回、ads.txtの内容と削除、既存SEOの回帰検査。
- `python tests/production_package_check.py`：本番を一時コピーで模擬してWrangler dry-run。外部公開はしません。
- `python tests/site_check.py`：35ルート×3幅、検索・カテゴリ・チェック機能・モバイル等。
- `python tests/adsense_live_check.py <URL> preview`：全36 HTMLのscriptなし、実ブラウザで広告リクエストなし、ads.txt404。
- 承認・本番deploy後に `python tests/adsense_live_check.py https://kaden-kaiketsu.com production` と既存live_seo_check.pyを実行。広告インプレッションを作らないよう本番のコード検査はHTML取得のみで、広告のクリックや表示テストは行いません。

## 残る操作

運営者がPR・プレビューを確認し、明示承認後にmainへマージ。本番deployと公開URLを検査します。その後AdSense管理画面でサイトの確認・審査リクエストを行います。Google側の審査承認・ads.txt認識・自動広告設定はリポジトリのテストでは確認できません。今回は自動広告や広告枠の設定を追加・変更しません。

## 公式出典

- https://support.google.com/adsense/answer/7584263?hl=ja
- https://support.google.com/adsense/answer/9274516?hl=ja
- https://policies.google.com/technologies/ads?hl=ja
