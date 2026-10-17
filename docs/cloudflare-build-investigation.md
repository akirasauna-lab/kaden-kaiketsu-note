# Cloudflareプレビュービルド失敗の調査（2026-10-17）

## 結論

GitHubでCloudflareの失敗は確認できましたが、原因を示すビルドログにはアクセスできていません。原因未特定のため、推測によるアプリ・ビルド設定の変更は行っていません。ローカルWorkers検査の合格を、Cloudflareクラウド上の公開成功とは扱いません。

## 確認した証拠

- [PR #1](https://github.com/akirasauna-lab/kaden-kaiketsu-note/pull/1) の対象コミット：`4be83bdbd8a76a2516619ecb1c59b7dc72e9da5a`。
- GitHub Check Runs API：`Workers Builds: kaden-kaiketsu-note` はcompleted / failure。
- Check Run ID：117317561443。Build ID：`2839b797-88fc-4617-a54e-29ac314ae39c`。
- GitHubのcheck outputにはBuild IDとScriptへのリンクだけで、エラー本文はなし。annotations_countも0。
- [Cloudflareの該当ログ画面](https://dash.cloudflare.com/38e24910b91d2c276ff8f405da8610f0/workers/services/view/kaden-kaiketsu-note/production/builds/2839b797-88fc-4617-a54e-29ac314ae39c) はブラウザでSign in to Cloudflareへ転送。
- `wrangler whoami` も未認証。Cloudflareの実ビルド環境・実行コマンド・環境変数・失敗段階は取得できていない。
- Vercelの成功チェックも存在するが、Cloudflareの成功を示すものではない。

## ローカルで再確認したこと

アプリコード・CSS・記事・noindex・ビルド設定を変更せずに再実行しました。

- `npm run check:deploy`：Wrangler 4.151.1、`python build.py`を含むdry-run成功。
- `python tests/build_check.py`：24 HTML、内部リンク・アンカー、canonical、noindex、下書きHTMLの除去などに合格。
- `wrangler dev --local` 上で `tests/site_check.py`：全13記事を含む23ルート×375/768/1440pxの69表示に合格。検索・6カテゴリ・コピー・保存・404・転送・noindexヘッダーも確認。
- CSS：`/assets/styles.css` がHTTP 200 / text/css。トップのボタンに既存の青（#1766aa）が適用されることをブラウザの計算済みスタイルで確認。
- 本番Cloudflare URLでの静的ファイル・CSS・記事表示は未確認。

## 管理画面で確認してほしい箇所

1. 上の「Cloudflareの該当ログ画面」に、該当アカウントでサインイン。
2. Worker名が `kaden-kaiketsu-note`、Build IDが上記のもの、コミットが `4be83bd` であることを確認。KURACALのWorkerは操作しない。
3. ログの最初のエラー（Error / failed / traceback等）と、その直前から最後の終了コードまでを取得。可能ならビルドログ全文をダウンロード。
4. WorkerのSettings → BuildのGit連携・ビルド設定も確認：リポジトリ、root directory、build command、deploy command、非本番ブランチ用のコマンド、Node/Python版。画面の名称が異なる場合はBuild設定欄を探す。
5. Build Variables and Secretsで、SITE_URL / OPERATOR_NAME / CONTACT_EMAILが設定されているかを確認。値や秘密情報をチャットへ貼る必要はなく、設定の有無だけでよい。
6. ログに出るトークン・パスワード等は伏せたうえで、最初のエラーと前後のログ・実行コマンドを共有する。その証拠に基づいて修正し、同じPRでCloudflare成功まで再確認する。

上の確認項目は原因の推定ではありません。Python依存・設定・認証等のどれが原因かは、ログを見るまで断定しません。現時点で再試行や設定変更をしても原因が確定したことにはなりません。

## 変更範囲

今回追加したのはこの調査記録だけです。KURACAL、既存デザイン、noindex、mainは変更しません。原因修正とCloudflare正常公開は、ログ取得まで未完了です。
