# 既存23記事のSEO・回遊改善（2026-11-01）

## 今回の範囲

新規記事は追加せず、既存23記事のJSON・タイトル・description・本文・URL・更新日を維持します。CSS/JS、AdSense publisher・生成条件・ads.txt、公開承認判定とSEO設定も変更しません。本番反映とmainマージは運営者の承認後です。KURACALは変更していません。

## トップと内部リンク

- 「よくあるお悩み」を冬の6症状へ変更。暖房不調、霜取り停止、湿度不足、加湿器の臭い、電気毛布、ヒーターに直接進む通常のaリンクです。JavaScriptが使えなくても記事を開けます。
- 検索の入力例と既存おすすめ枠の紹介文を冬向けに変更。既存の白・青の部品とレイアウトを使います。
- `config/navigation.json` に冬向け導線と23記事の関連記事をまとめます。既存記事内の旧related_slugsは本文データ保全のため残しますが、生成には新設定を使います。
- Fire TV、Netflix、SwitchBot、加湿器は同じ機器・サービス内を優先。Chromecastの接続記事はカテゴリをまたいで相互リンク。暖房の効きと霜取り停止も相互リンクします。
- 別メーカー・別機器のカードには対象差と手順をそのまま流用しない注意を明記し、元々のブランド表示も維持します。
- 洗濯機は関連する別記事がまだないため、無関係な記事を追加表示しません。トップとカテゴリからの導線は維持します。
- 自己リンク・関連記事内の重複・存在しないslug・4件以上の関連記事はビルド時に拒否。下書きへのリンクは出力しません。ヘッダー/本文/フッター等、役割の異なる同一URLへのリンクは必要な導線として維持します。

## GA4の本番確認

全36 HTMLの公開ソースにGA4/GTMのローダーや測定IDは見つかりませんでした。トップページの広告通信を遮断したブラウザ確認でも、GA4通信とgtag/google_tag_managerのグローバルを確認できません。リポジトリにもGA4設定はありません。

**GA4は未設置と判断し、このサイト用の測定ID取得・指定待ちです。** Google Analytics管理 → データストリーム → https://kaden-kaiketsu.com のウェブストリーム → G-から始まる測定IDを確認してください。ストリームがなければサイト用のウェブストリームを作成します。プロパティID・AdSense publisher IDで代用しません。今回はタグを追加していないため、GA4のイベント受信やリアルタイム計測は検証できていません。AdSenseは別途本番で従来どおり確認します。

公式: https://support.google.com/analytics/answer/12270356 、https://support.google.com/analytics/answer/9539598

## 技術的SEO：確認済みと要対応

本番HTTPSのcanonical・sitemap・robots・HTML/HTTP noindexを検査します。公開対象は35 URL（トップ・23記事・8カテゴリ・運営情報3ページ）で、404はnoindexを維持します。プレビューは従来のnoindex/Disallow/sitemap非公開を維持します。

**本番HTTPは301ではなく200を返しています。未解決事項です。** PlaywrightのGET（転送追従なし）とcurlの両方でトップ・記事を確認しました。HTTPS canonicalだけでHTTP転送が実装されたとは扱いません。

Workersの静的アセット専用構成を維持するため、リクエストごとに実行するWorkerや非対応のドメイン単位_redirectsルールを追加していません。Cloudflare側でHTTPSへの転送を有効化する操作が別途必要です。承認前に管理画面設定は変更していません。

### 承認後のHTTP→HTTPS対応

1. Cloudflareで **kaden-kaiketsu.comのゾーン** を選び、SSL/TLS → Edge Certificatesへ進む。
2. Always Use HTTPSを有効にする。SSL/TLSがOffの場合は既存のHTTPS構成を確認してから対応する。
3. `python tests/http_redirect_check.py` を実行し、トップ・記事・クエリ付き記事で、最初の応答が301かつ同じパス/クエリのHTTPS URLになっていることを確認する。
4. 転送先のHTTPSが200で、ループがないことと、AdSense・ads.txt・SEO・プレビューの状態を再検査する。

このチェックは現在の本番では失敗します。ビルドやプレビュー検査が成功しても、HTTP→HTTPSの修正完了とは報告しません。Always Use HTTPSはゾーン全体に作用するため、設定対象をこのサイトのゾーンに限定します。

公式: https://developers.cloudflare.com/ssl/edge-certificates/additional-options/always-use-https/ 、https://developers.cloudflare.com/workers/static-assets/redirects/

## 検査

- build_check.py：全36 HTMLの内部リンク・アンカー・canonical、関連記事設定の不正入力拒否、本番/preview/dev/他ブランチのSEOとAdSense判定。
- production_package_check.py：本番用条件を一時コピーで模擬しWrangler dry-run。
- site_check.py：35ルート×375/768/1440px。6本の冬リンク、全関連記事の順序・別対象注意、冬の検索、全カテゴリ、保存・コピー・モバイルメニュー。
- live_seo_check.py、adsense_live_check.py：実プレビューと現本番を別々に検査。広告の表示・クリックはテストしません。
- http_redirect_check.py：別途Cloudflare設定後に301を検査するチェック。現在の失敗は上記の既知課題です。

GA4やSearch Consoleのデータを取得していないため、検索順位・表示回数・PV・CTRの改善効果は未確認です。数値を根拠にしたタイトルの一括変更は行っていません。
