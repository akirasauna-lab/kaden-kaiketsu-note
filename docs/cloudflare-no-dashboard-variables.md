# Cloudflareの追加環境変数なしで検索公開する

この手順が現在の仕様です。以前のSITE_URL / SITE_BUILD_TARGET / CONTACT_EMAIL / OPERATOR_NAMEを手動登録する説明は不要になりました。Runtime variablesもBuild variablesも追加しません。

## 保存済みの値

- `config/publication.json`：承認true、正式URL `https://kaden-kaiketsu.com`
- `config/operator.json`：家電の解決ノート編集部、`akirasauna@gmail.com`

上記だけを生成元とします。同名の古い環境変数が残っていても設定値を上書きしません。13記事、CSS/JS、問い合わせ先の値は変更していません。canonicalを正式URLへ統一するため、生成HTMLのheadのURL情報は更新されます。

## 本番の判定

以下をすべて満たすときだけ公開対象のindexを有効化します。

1. publication.jsonの承認がtrue。
2. Cloudflareが自動注入する `WORKERS_CI=1`。
3. Cloudflareが自動注入する `WORKERS_CI_BRANCH=main`。
4. Wranglerのビルド識別値が `WRANGLER_COMMAND=deploy`。
5. Linuxのプロセス情報から、実際のWrangler起動コマンドがdeployだと確認できる。
6. 保存済みURL・運営情報が有効。

preview/dev/他ブランチ/ローカル実行/識別情報なしはnoindex。main本番を示す自動情報があるのに実コマンドが不明なら例外でビルドを停止し、公開しません。

`WRANGLER_COMMAND`だけでは判定しません。固定しているWrangler 4.151.1のpreviewハンドラーは、内部のgetEntryにdeployを渡すため、previewでもこの値がdeployになり得ます。実装の確認箇所は `node_modules/wrangler/wrangler-dist/cli.js` のpreviewHandler → getEntry(..., "deploy")と、runCommandの環境注入です。Wranglerを更新するときはこの挙動とプロセス検出を再検査してください。

実コマンドはCloudflareのLinux上の `/proc` を読み、最も近いWrangler Nodeプロセスのargvを確認します。読み取り不可、未知の起動形式、別OSなどで推測はしません。Cloudflareでこれが利用できない場合、本番公開を停止するため、管理画面で手動の「本番フラグ」を足して回避しないでください。

公式根拠：

- [Workers Buildsの既定変数](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/#default-variables)：WORKERS_CIとWORKERS_CI_BRANCHはCloudflareが注入。
- [Wranglerのカスタムビルド](https://developers.cloudflare.com/workers/wrangler/custom-builds/#wrangler_command-environment-variable)：ビルド時にWRANGLER_COMMANDが渡る。
- [Workersビルドイメージ](https://developers.cloudflare.com/workers/ci-cd/builds/build-image/)：Linuxビルド環境。

これらはビルド時の情報です。静的アセット専用Workerにruntime bindingsを追加する必要はありません。

## 出力とHTTP

| 環境 | 公開対象HTML | sitemap | robots | HTTP noindex |
|---|---|---|---|---|
| 検証できたmain本番deploy | index,follow | 正式URLの23ページ | Allow + 正式sitemap | 公開対象への一律noindexなし |
| プレビュー・開発・他ブランチ | noindex,nofollow | なし | Disallow | 全体に付加 |

404・検索除外HTMLは本番でもnoindex。下書きは配信から外れます。`.well-known/publication.json` は秘密情報を含まないビルド状態確認専用ファイルで、常にHTTP noindexです。診断JSON、404、下書き、検索除外、空カテゴリはsitemapに含めません。

この診断ファイルはモード・ブランチ・実コマンド・Wranglerビルド識別値だけを出します。トークンや全環境変数を公開しません。main本番公開後は `indexing_enabled: true`、プレビューはfalseであることを確認できます。

## 検査方法と確認範囲

- `python tests/build_check.py`：コマンド解析とLinuxプロセス情報のモデル、main/preview/dev/別ブランチ/情報不足、古い手動変数の無視、sitemap/robots/canonical/ヘッダー、問い合わせ先、下書き除外。
- `python tests/production_package_check.py`：一時コピーでmainの本番条件をシミュレーションし、生成結果をWrangler deploy --dry-runでパッケージ検査。外部には公開しません。WindowsではLinuxの観測部分だけをテスト内で代用します。
- `npm run check:deploy`：現在のローカル実行は本番と判定せずnoindex。
- PR #3のCloudflareプレビューで、実際のブランチ・実コマンド・noindex・CSS・13記事等を確認します。

mainへのマージ前のため、今回の新コードを使ったCloudflare本番deployそのものは未実施です。本番の検証を済ませたという意味にはしません。シミュレーションと実プレビューを区別して報告します。

## 追加設定が必要か

SITE_URL等の手動変数追加は不要です。既存のGit連携がこのリポジトリを使い、本番ブランチmain・本番コマンド `npx wrangler deploy`・プレビューコマンド `npx wrangler preview` になっている前提を維持します。専用ドメインのDNS/TLSとWorkerへの接続は別の既存設定で、環境変数で代替できません。

以前の手動変数は読みません。Cloudflareが自動で渡すWORKERS_CI等は自分で上書きしないでください。Git連携のないローカルmainからのdeployは本番と確認できないため検索公開しません。

## マージ後の検索公開手順

1. PR #3の内容を最終確認し、ユーザーの指示に従ってmainへマージする。今回は未マージ。
2. 既存Cloudflare Git連携によるmainビルドを待つ。カスタムビルドが新しいHTMLを生成してからdeployする。
3. ログの `Publication context` と正式ドメインの `/.well-known/publication.json` で、workers_ci=true / branch=main / actual_wrangler_command=deploy / indexing_enabled=trueを確認。
4. `https://kaden-kaiketsu.com` のトップ・13記事・カテゴリ・運営ページ・CSSを検査。HTMLとレスポンスヘッダーにnoindexが残らず、canonicalが正式URLであることを確認。
5. `/robots.txt`のAllowとsitemap行、`/sitemap.xml`の23 URL、404・検索除外のnoindexを確認。プレビューURLでは引き続きnoindexであることも確認。
6. Search Consoleで所有権確認後にsitemapを送信し、URL検査で確認する。登録や収益は保証しない。

本番コンテキストを判定できず失敗した場合は、ビルドログを確認して停止原因を調べます。インデックスのガードを外す修正やmainへの追加マージを推測で行いません。
