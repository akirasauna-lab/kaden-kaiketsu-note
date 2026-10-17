# robots.txtとSearch Consoleの確認（2026-10-17）

## 本番で確認した内容

https://kaden-kaiketsu.com/robots.txt はHTTP 200・text/plainで次を返しています。

```text
User-agent: *
Allow: /
Sitemap: https://kaden-kaiketsu.com/sitemap.xml
```

通常・Googlebot・Google-InspectionToolのUser-Agentで同じ許可内容を確認しました。ただしGoogleの実IPからの取得やSearch Consoleのライブテストそのものは、この検査では確認できません。

今回の取得ではブロック状態を再現していないため、過去のエラー原因を断定しません。Googleは通常robots.txtを最大24時間キャッシュし、再取得に失敗するとそれ以上保持する場合があります。キャッシュ残存は可能性であり、確認済みの原因ではありません。

出典: https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec

## 変更と配信元

- 未使用のリポジトリ直下robots.txt（旧Disallow）を削除し、重複を整理しました。Wranglerはassets.directory=./siteなので、この旧ファイルが現在の本番をブロックしていたという証拠はありません。
- 生成処理は既存の安全な判定を維持します。承認済みmainの実deployだけAllow、他の環境はDisallowとHTML/HTTPのnoindexです。
- build_check.pyで配信ディレクトリ、旧ファイルの再混入、全canonicalへのGooglebot/InspectionToolの許可・拒否を検査します。
- live_seo_check.pyで配信後のトップ＋13記事、23件のsitemap、canonical、HTMLとHTTPヘッダーを検査できます。本番とプレビューは別モードです。
- デザイン・記事・問い合わせ先・公開承認条件は変更しません。HTTPキャッシュは本番でpublic, max-age=0, must-revalidateを確認済みで、推測による変更は加えません。

## 運営者の再確認

1. Search Consoleで検査したURLが `https://kaden-kaiketsu.com/` と一致するか確認してください。httpやwwwはrobotsの適用範囲が異なります。
2. robots.txtレポートで最終取得時刻と取得内容を確認し、古いDisallowなら再クロールをリクエストしてください。
3. URL検査のライブテストをトップと記事で再実行してください。成功後にインデックス登録をリクエストし、正式sitemapを送信してください。
4. 同じ失敗が続く場合は、失敗時刻・対象URL・レポートのrobots取得内容を記録し、CloudflareのSecurity Eventsで該当時刻のGoogleクローラーの遮断有無を調べてください。検証なしに保護設定を無効化する必要はありません。

PRは運営者の確認後にマージします。追加の環境変数は不要です。マージ後はmainのCloudflare deploy成功を確認し、上記の本番検査を再実行してください。
