# 冬向け10記事の公開前レビュー（2026-10-24）

## 範囲

既存13記事の元データとURLは維持。暖房3・加湿器3・電気毛布/ヒーター2・Netflix2を追加し、合計23記事にします。冬季中心の8本と通年のNetflix2本です。CSS・JS・テンプレートのレイアウトは維持し、既存のカテゴリ部品に加湿器・暖房器具を追加します。トップの既存カード枠は暖房・加湿・電気毛布を優先し、記事一覧は更新日順です。

| slug | 意図・重複の区別 | 照合した公式情報 |
|---|---|---|
| daikin-heating-not-warm | 風は出るが寒い。既存の冷房不調と区別 | ダイキン knowledge3007 |
| daikin-heating-defrost-stops | 途中の温風停止・再開。効きの弱さと区別 | ダイキン knowledge2841、3007 |
| hisense-heating-outdoor-water | 室外機の水・湯気。室内漏水とは区別 | ハイセンス FAQ21 |
| panasonic-humidifier-low-humidity | 水の減りと加湿能力・使用環境 | パナソニック FAQ77659、選び方、11854 |
| panasonic-humidifier-filter-smell | 臭い・白い固まりの手入れ | パナソニック FAQ77665、11854 |
| panasonic-humidifier-water-lamp | 給水後も消えない表示 | パナソニック FAQ11907 |
| koden-electric-blanket-not-warm | 接続と点検。コントローラー流用禁止 | 広電 FAQ共通・電気毛布 |
| panasonic-ceramic-heater-stops | 人センサー・目詰まり・傾き等の停止 | パナソニック FAQ62100 |
| netflix-tv-no-sound | 映像は動き無音。既存のフリーズとは区別 | Netflix468、372 |
| netflix-tv-subtitles-missing | 字幕の選択と表示不具合 | Netflix372、23439 |

公式URLは各記事のsourcesに掲載。全記事に結論、症状別原因、手順、故障を断定せず点検へ進む基準、FAQ、対象範囲、資料照合日、実機未検証を表示します。暖房の停止時間や復帰操作を全型番共通とせず、洗剤の濃度や部品の適合も機種の説明書優先です。換気停止、霜への熱湯、機械内部の分解、センサーの固定、別コントローラーの流用は推奨しません。

## 検査と限界

- build_check.py：36 HTML（404含む）の内部リンク・アンカー・canonical、本番35 URLのsitemap、preview/dev/他ブランチのnoindexを検査。
- production_package_check.py：Windowsのため実際のLinuxプロセス観測は一時コピーで模擬。本番候補のWrangler dry-runを行い、承認前の外部本番デプロイはしません。
- site_check.py：35ルート×375/768/1440px、23記事、8カテゴリ、検索・モバイルメニュー・チェック機能等を検査。
- live_seo_check.py：Cloudflare実プレビューでnoindex/Disallow/sitemap404、承認後の本番でindex許可・35 URL sitemap・canonical・全記事200を検査します。
- 全記事の出典32 URLをGET。新規記事の出典はすべて200。既存のSwitchBot公式6 URLは403のため現環境では到達性未確認です。404/410は検出していません。既存記事の出典を推測で差し替えていません。
- 実機検証、Googleによる実クロール、検索順位・AdSense収益は未確認です。

## 承認後

PRのプレビューと検査結果を運営者が確認し、承認後にmainへマージ。Cloudflareのmain deploy完了を確認して、実本番の新規10 URLとsitemapを再検査します。承認までは本番公開しません。KURACALへの変更はありません。
