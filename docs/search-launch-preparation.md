# Google検索への正式公開準備（2026-10-17）

## 現在の状態

検索公開はまだ承認されていません。`config/publication.json` の `indexing_approved` はfalse、production_originは未確定です。HTMLとCloudflare静的レスポンスのnoindexを維持します。13記事と白・青のCSSは変更していません。運営者表示名は「家電の解決ノート編集部」を仮設定し、問い合わせ先は「準備中」と表示します。架空のメールアドレス・AdSense ID・Search Console確認コードは作成しません。

## 実装した切り替え条件

次の条件がすべてそろった場合だけ検索公開用HTML・robots・sitemapを生成します。

1. 明示承認後に、`config/publication.json` の `indexing_approved` を真偽値trueへ変更する。
2. 同ファイルの `production_origin` とビルド環境の `SITE_URL` が、正式なHTTPS originで完全一致する。
3. 本番ビルド環境に `SITE_BUILD_TARGET=production` を設定する。
4. `wrangler deploy` のカスタムビルドとして実行され、Wranglerが渡す `WRANGLER_COMMAND` が `deploy` である。
5. 実在する問い合わせメール `CONTACT_EMAIL` と運営者表示名がそろう。欠けていれば検索公開用ビルドを失敗させる。

環境変数だけでは解除できません。通常の `python build.py`、`wrangler dev`、`wrangler preview`、SITE_BUILD_TARGET未設定、承認falseではnoindexです。プレビューでは本番向けの環境変数や承認済みファイルがあっても、Wranglerのpreviewコマンドによってnoindexを強制します。WRANGLER_COMMANDを手動で偽装する運用はしないでください。

設定ファイルに問い合わせ先を作りません。実在するメールを確定してからビルド変数へ指定します。問い合わせフォームを使いたい場合は、このメール用ガードと運営情報表示を別途改修してください。

## 生成内容

| 項目 | 現在・プレビュー | 承認後の本番deploy |
|---|---|---|
| HTML meta robots | noindex,nofollow | 公開対象はindex,follow、404や対象外記事はnoindex,nofollow |
| Workers `_headers` | X-Robots-Tag: noindex, nofollow | 全体へのnoindexヘッダーを取り除く。404や検索対象外はHTML側noindexを維持 |
| canonical | SITE_URLがなければ省略。あれば指定正式originを参照 | 正式origin＋末尾スラッシュ付きの自己参照。404はcanonicalなし |
| robots.txt | 既存のDisallow: /を維持 | Allow: /と正式sitemapの絶対URL |
| sitemap.xml | 生成しない。古いファイルを削除 | 下記の公開対象URLからXMLを自動生成 |

公開対象はトップ、about/editorial/privacy、`official-reviewed`の表示対象記事、中身のあるカテゴリです。記事を`review_status: draft`にすると配信HTMLも削除します。記事を表示したまま検索対象外にする場合は`search_visible: false`にできます。未再確認の記事・空カテゴリ・404・検索UIの状態・旧ルート配布物はsitemapに入れません。現在の13記事では本番シミュレーションのsitemapは23 URLです。記事のlastmodは実際のデータのmodifiedを使用し、ビルド日を機械的に付けません。

Googleはcanonical URLの絶対URLをsitemapに載せることを案内しています。送信してもインデックスは保証されません。[Googleのsitemap説明](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

Cloudflareのプレビュー基盤もX-Robots-Tag: noindexを付加することを、前回の実URLで確認済みです。今回のPRでも実URLで再確認します。正式公開時は基盤側の追加ヘッダー、Rules、キャッシュも含めて確認が必要です。robotsのDisallowだけでは検索非掲載を保証せず、noindexをGoogleに読ませるにはクロール可能である必要があります。[Googleのnoindex説明](https://developers.google.com/search/docs/crawling-indexing/block-indexing?hl=ja)

## 運営情報と方針

- 表示名は環境変数OPERATOR_NAMEの既定値として「家電の解決ノート編集部」。正式公開前にこの名称で確定するか判断してください。
- 問い合わせ先未設定時は準備中と表示。設定した実メールはabout/privacy/editorialへ反映します。
- プライバシーポリシーに配信基盤Cloudflareでリクエスト情報が処理される場合があることを明示。検索・チェックはブラウザ内処理であることを区別しました。
- 広告・解析は未導入のまま。利用中でないGoogle広告Cookieやオプトアウトを、導入済みの事実として掲載していません。
- 編集方針に資料照合と実機検証の区別、確認範囲、訂正と更新日の扱いを追加しました。

## 公開前にユーザーが決めるもの

1. 正式ドメイン（HTTPS origin）。独自ドメインにする場合は取得・DNS・Cloudflareカスタムドメイン設定を行う。
2. 公開する実在の問い合わせメール。受信可能であることを確認する。
3. 運営者表示名の確定。
4. main向けPRのレビューとマージの承認。今回こちらではmainへマージしない。
5. noindex解除の明示承認。今回は解除しない。

## 承認後の公開手順

- 先に問い合わせ先・表示名・ドメインを確定する。
- 公開承認用の変更としてproduction_originとindexing_approvedを設定し、別途レビューする。
- Workers本番のビルド変数へSITE_BUILD_TARGET=production、SITE_URL、CONTACT_EMAIL、必要ならOPERATOR_NAMEを設定する。プレビュー側はSITE_BUILD_TARGET=previewまたは未設定のままにする。
- 本番ブランチはmain、非本番ブランチ用コマンドはwrangler previewであることを確認する。プレビュー用コマンドをdeployへ置き換えない。
- Workers Buildsの依存インストールでPython requirementsとnpm依存をそろえ、wrangler deployが最新HTMLを生成する。
- 公開後にHTML meta、HTTP X-Robots-Tag、robots、sitemap、canonical、HTTPS・ホスト転送、404、CSS、全記事を正式URLで検査する。公開対象ページにnoindexが残っていないか、プレビュー側には残るかを両方確認する。
- 撤回時は承認falseへ戻し再ビルド・再デプロイする。生成済みHTMLをそのまま再利用しない。検索結果への反映は即時保証されない。

## Google Search Consoleの登録手順

1. 正式ドメイン確定後にSearch Consoleでプロパティ追加。ドメインプロパティならDNS TXTによる所有権確認を選ぶ。独自ドメインのDNSを管理できない場合は、正式HTTPS URLプレフィックスと利用可能な確認方法を選ぶ。
2. Googleが実際に発行したTXT値や確認コードだけを使う。ここではコードを作らず、DNS変更・アカウント登録も行わない。
3. DNS TXTを確認して所有権確認。値を確認後も保持する。[所有権確認の公式手順](https://support.google.com/webmasters/answer/9008080?hl=ja)
4. noindex解除と正式公開の確認後、サイトマップ欄で `/sitemap.xml` を送信。取得成功と検出URLを確認する。[サイトマップレポート](https://support.google.com/webmasters/answer/7451001?hl=ja)
5. URL検査でトップ・各カテゴリ・代表記事をライブテストし、canonicalとインデックス可否を確認して必要なら登録をリクエストする。全記事を何度も再申請する運用はしない。
6. インデックス未登録の理由、404、検索クエリ・表示・クリックを定期確認。登録やsitemap送信が検索順位を保証するわけではない。

## AdSense申請前の不足項目

| 項目 | 状態・次の対応 |
|---|---|
| 正式URLと所有権 | 未確定。正式URLでサイトを管理できることを確定 |
| 連絡先・運営者 | 表示名は仮、メール未確定。実際に使える窓口を整備 |
| 本番公開 | 未承認・noindex中。Google検索への公開判断とAdSense申請は別途実施 |
| 内容の独自性・有用性 | 13記事を維持。公式要約だけで十分な価値と決めつけず、対象を絞る切り分けや確認記録を改善。実機体験を創作しない |
| 申請者の資格 | AdSenseアカウントの要件・年齢・所有権等を申請者が確認。未確認 |
| 広告用プライバシー記載 | 導入前にGoogle等のCookie、配信事業者、パーソナライズ広告の選択方法を実態に合わせて追加 |
| 地域に応じた同意管理 | 実際の対象地域とGoogleポリシーを確認し、必要な同意管理を実装してから広告を配信 |
| サイト確認・広告コード | 実アカウントから取得した方法で接続。未発行のIDやタグを作らない |
| ads.txt | 実パブリッシャーID発行後に対応。Googleは強く推奨しているが一律の必須申請条件とは扱わない |
| 広告の配置 | 安全注意・結論・チェック操作・公式リンクを妨げない。広告と操作ボタンを区別 |

13記事あれば承認される、何PVあれば申請できる、といった独自の足切り基準は設けません。月1万円は目標であり、承認・収益・達成時期の保証ではありません。公開後はSearch Console、広告導入後は実測ページRPMとPVで判断します。

公式参照：[AdSense資格要件](https://support.google.com/adsense/answer/9724?hl=ja)、[プライバシー必須コンテンツ](https://support.google.com/adsense/answer/1348695?hl=ja)、[ads.txt](https://support.google.com/adsense/answer/12171612?hl=ja)。申請直前にも最新要件を確認してください。
