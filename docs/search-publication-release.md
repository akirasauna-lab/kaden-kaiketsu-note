# 正式検索公開の最終確認（2026-10-17）

> 手動のビルド変数追加は廃止しました。[追加環境変数なしの最新仕様](cloudflare-no-dashboard-variables.md) を参照してください。以下には過去の手順を含みます。

## 確定内容

- 正式URL： https://kaden-kaiketsu.com
- 運営者：家電の解決ノート編集部
- 公開問い合わせ先：akirasauna@gmail.com
- Google検索公開：ユーザー承認済み
- mainへのマージ：最終確認待ち。今回実施しない。

`config/publication.json` に承認trueと正式originを設定。`config/operator.json` に公開用の運営情報を保存し、about/editorial/privacyへ同じ値を表示します。このメールアドレスはユーザーがサイトとPRで公開するよう指定した情報です。

## 公開とプレビューの区別

プレビュー・通常ビルドはnoindexのままです。コミットしたsite/も公開前確認用のnoindex版です。本番設定をそろえてwrangler deployした際に、公開対象のindex,follow、正式canonical、23 URLのsitemap、AllowとSitemap行を持つrobots、全体noindexを除いた_headersを生成します。404・検索除外はnoindexを維持します。

運営情報のデフォルト表示は公開用設定から行いますが、本番のCONTACT_EMAILとOPERATOR_NAMEは明示設定が必要です。設定ファイルと異なる値でもビルドを停止させ、古いビルド変数で別の連絡先が掲載されることを防ぎます。

## Cloudflareで行う操作（本番公開前に必要）

対象はWorker `kaden-kaiketsu-note` のみです。KURACALのWorkerや設定は変更しません。

1. Cloudflare → Workers & Pages → kaden-kaiketsu-note → Settings → Build。
2. Build variables and secretsに次を設定する（実行時のVariables & Secretsだけでは不可）。

| 変数 | 値 |
|---|---|
| SITE_URL | https://kaden-kaiketsu.com |
| SITE_BUILD_TARGET | production |
| CONTACT_EMAIL | akirasauna@gmail.com |
| OPERATOR_NAME | 家電の解決ノート編集部 |

3. Gitリポジトリが `akirasauna-lab/kaden-kaiketsu-note`、本番ブランチがmainであることを確認。
4. build commandはPython依存をインストールできる設定、deploy commandは `npx wrangler deploy`、非本番preview commandは `npx wrangler preview` を維持。WRANGLER_COMMANDは自分で設定せずWranglerに任せる。
5. Domains & Routesで `kaden-kaiketsu.com` がこのWorkerに接続され、DNS/TLSが有効か確認。
6. 設定の保存だけで公開完了とはしない。PRの最終レビュー後、明示指示に従ってmainへマージし、本番ビルド結果を確認する。

こちらのCLIは `wrangler whoami` が未認証です。本番のビルド変数・ドメイン設定の保存状態を取得・変更できていないため、本番公開作業は停止しています。秘密のAPIトークンやGmailパスワードをチャットに貼る必要はありません。

参考：[Cloudflareビルド設定](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/)

## 実施した検査

- build_check.py：承認ガード、問い合わせ先・運営者名不足／不一致、プレビュー強制noindex、sitemap対象、下書き削除、canonical等の回帰検査に合格。
- 正式URL・確定連絡先を使った本番ビルドを作業用の別コピーで生成。23 canonical URL、13記事、sitemap、robots、全体noindexヘッダーの除去、3ページのmailto、404 noindexを確認。これは外部への公開ではありません。
- Wrangler deploy --dry-run成功。正式設定を入れていない通常チェックではindexing=Falseを確認。
- 13記事の元データと白・青のCSS/JSは変更しない。

## マージ・デプロイ後の確認項目

正式URLのトップ・13記事・6カテゴリ・運営3ページ・CSS/JSを確認します。特に次を満たす必要があります。

- 公開対象はHTTP 200、metaがindex,follow、HTTPヘッダーにnoindexが残っていない。
- canonicalはhttps://kaden-kaiketsu.comの各末尾スラッシュURL。
- /sitemap.xmlは公開対象23 URLのみ、/robots.txtはAllowと正式sitemap URL。
- 404と検索除外ページはnoindex。プレビューはmetaとHTTPヘッダーのnoindexを維持。
- 検索、内部リンク、375px表示、3ページの問い合わせ先が正しい。

その後、Search Consoleで正式ドメインの所有権を確認しsitemapを送信します。AdSenseは別途、実アカウントの申請・サイト確認、広告用のプライバシー記載、必要な同意管理、実IDのads.txtなどを整えます。検索登録・審査承認・月1万円の収益は保証されません。
