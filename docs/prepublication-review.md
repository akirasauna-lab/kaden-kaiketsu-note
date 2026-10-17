# 公開前品質確認（2026-10-17）

> SEO切り替えの最新仕様は [Google検索への公開準備](search-launch-preparation.md) を参照してください。以下には以前の固定noindex仕様の記録を含みます。

対象：`akirasauna-lab/kaden-kaiketsu-note`。ブランチ：`content/troubleshooting-strategy-20261017`。この記録は前回の `content-strategy.md` に残した「既存10記事は未再照合」という状態を更新するものです。

## 結果

13記事すべてを本文・FAQ・適用範囲・公式出典と照合し、修正しました。全記事に結論、症状別原因、確認手順、改善しない場合の相談、公式出典、資料照合日、実機未検証を掲載。資料確認は実機での解決や全世代の動作保証を意味しません。参照資料で確認できない全型番のUI・互換性は適用範囲欄で未確認と明示しています。

## 記事別の確認記録

確認日は全件2026-10-17。下記の公式本文を読み、該当記事に使う主張を照合しました。出典サイト全体や全リンク先を検証したという意味ではありません。各記事の具体的な参照URLは `content/articles.json` と `article-review.json` に記録。

| 記事slug | 主な公式本文・照合箇所 | 修正・確認結果 |
|---|---|---|
| fire-tv-wifi-connect | Amazon英語版「Can't Connect Your Fire TV Device to Wi-Fi」「During Setup」、Amazon Japanの接続方法 | 診断・再起動・再接続を照合。英語版と明記、日本向け全世代の画面差は未確認。安易な初期化の誘導を相談へ変更 |
| fire-tv-no-picture | Amazon Japan「Fire TV Stickをテレビに接続する方法」の接続・無映像・再起動 | 入力、HDMI、給電を照合。同梱品・USB給電の一般化を避ける。別テレビへの接続での故障断定を削除し、症状を記録して相談へ |
| fire-tv-remote-unresponsive | Amazon英語版「Fire TV Remotes」、Amazon Japanの接続方法 | 電池・距離・再起動・ペアリングを照合。世代別リセットは案内せず、スマホ代用時の同一Wi-Fi条件を明記 |
| chromecast-device-not-found | Google「キャストするデバイスが見つかりません」「詳細: キャスト時のローカルネットワーク」 | 同一ネットワーク、権限、再起動を照合。iOS 14以降の権限位置を明記。YouTube固有原因は未確認と明示 |
| chromecast-wifi-setup | Google「Chromecast または Google TV Streamer を Wi-Fi に接続できない」「Wi-Fiが表示されない」 | 距離・帯域・AP分離・設定方式を照合。Google Homeを全機種必須とするような記述を修正。初代2.4GHz限定は公式本文で確認 |
| switchbot-hub2-wifi | SwitchBot「Hub 2はインターネット接続ができない」「Hub 2の赤外線リモコンのローカル操作機能について」 | ハブ2と2.4GHzの範囲を照合。再起動で機能停止する点、ローカル操作の事前設定・登録方式・Bluetooth範囲の条件を明記 |
| switchbot-bot-not-working | SwitchBot「ボットが接続できない場合」「ボットをハブミニ/ハブ2に接続する方法」、英語版ボットオフライン | 電池・近距離・ハブ登録を照合。ボットChargeを対象外に。アプリV9.0以降のクラウドサービス手動設定不要を反映。機械的な不具合の推測を減らし、相談に必要な情報へ変更 |
| switchbot-ir-remote-register | SwitchBot「ハブミニで家電リモコンを追加できない」の適用製品・赤外線方式・学習方式・設置 | 記事名はハブミニだが公式本文の適用製品にハブ2等もあることを確認。未対応Bluetoothボタン・全ボタン互換性を明確化。非関連のローカル操作出典を削除 |
| iphone-wifi-unavailable | Apple「iPhoneやiPadでWi-Fiに接続できない場合」 | Wi-Fi・機内モード・別端末・リセット影響を照合。VPN/APN等への影響を明記。リセット実行手順は案内せず、管理端末は管理者へ |
| windows-wifi-trouble | Microsoft「WindowsでWi-Fi接続の問題を修正する」のWindows 11・一般的な確認 | Windows 11のGet Help診断へ修正。Windows 10の「状態」画面と混同させない。ドライバー削除・初期化の操作は案内しない |
| netflix-tv-freezes | Netflix「Netflixがフリーズする…が、デバイスは機能する」のテレビ別案内 | Sony Android TV向けはアプリ更新、他社でログアウトが案内される場合は再ログインと分けた。テレビ全体が無反応は対象外 |
| panasonic-topload-spin-vibration | Panasonic「タテ型洗濯機・脱水時の振動が大きい」の衣類・設置・排水・すすぎ補正 | 縦型限定を再確認。エラーを他社へ流用しない。重い本体移動や届かない排水口作業を自己実施させない |
| daikin-aircon-not-cooling | ダイキン「冷えない、冷たい風が出ない（ルームエアコン）」の設定・風路・フィルター・点検 | 冷房限定で再照合。高所、分解、冷媒作業なし。電源リセットは専用回路が不明なら相談とする |

Amazonの日本向けカスタマーサービスのリンク先を一部取得できない場合がありました。そのリンク先の本文を確認済みとはしていません。今回、読めたAmazon Japanの公式解説と英語版公式ヘルプを出典として区別して記録しています。

## サイトとビルド

- 13記事、6カテゴリ、トップ、方針3ページ、404の計24 HTMLを生成。全ページh1、内部ファイルリンク、ページ内アンカー、noindexを検査し合格。
- Chromeでトップ＋13記事＋6カテゴリ＋方針3ページの23ルートを375/768/1440pxで確認。計69表示でHTTP 200、横はみ出しなし。実スマホ実機・Safariは未確認。
- 6カテゴリの件数と表示、症状検索、全角英数字の正規化、ゼロ件・解除、モバイルメニュー、チェックの再読込保持・解除・クリップボードコピーを確認。JavaScript例外なし。
- Cloudflare Wrangler 4.151.1 の `deploy --dry-run` がカスタムビルド込みで成功。`wrangler dev --local` のworkerd上で上記ブラウザ検査を実施。
- Workersローカル環境で不明URLは404、末尾スラッシュなしはスラッシュありへ307、X-Robots-Tagはnoindex,nofollow、robots.txtはDisallow、sitemap.xmlは404を確認。
- 下書きに戻した記事の古いHTMLが残る問題を修正し、再ビルド時に配信対象から消える回帰検査を追加。
- CSSは変更していません。白・青の外観を維持。モバイル記事冒頭・原因節・PCトップのスクリーンショットも確認。

検査コマンド：`python tests/build_check.py`、`python tests/site_check.py`（`SITE_TEST_URL`をWorkersローカルURLに設定）、`npm run check:deploy`。

## SEO

| 項目 | 現在の処理・確認 | 正式な検索公開時に必要なこと |
|---|---|---|
| noindex | HTMLとWorkersの `_headers` で維持。SITE_URLを指定しても外れない | 解除の承認後に、metaとX-Robots-Tag両方を見直す |
| robots.txt | 既存のDisallow: /を維持 | Googleがnoindexを読むにはクロールが必要。検索非掲載を保証するアクセス制限ではないことに注意し、公開方針に応じて設計を決める |
| sitemap.xml | noindexのURLを列挙しないよう、現時点は生成停止。古いファイルも削除 | 正式ドメイン確定・インデックス許可後に、対象200/canonical URLのみで再実装しrobotsに案内を追加 |
| canonical | ドメイン未設定時は省略。仮ドメインを実データとして出さない。テスト用originでは各ページの自己参照が正しいことを検査 | SITE_URLを正式HTTPS originに設定し本番レスポンスで確認。workers.devと独自ドメインの重複整理 |
| 404 | canonicalなし。Workersで404応答 | 本番でも404応答を確認 |
| URL正規化 | force-trailing-slash、canonicalも末尾スラッシュ。パス・クエリ・認証情報入りSITE_URLを拒否 | 独自ドメインのHTTPS・ホスト転送とあわせて確認 |

[Googleのnoindex説明](https://developers.google.com/search/docs/crawling-indexing/block-indexing?hl=ja)では、Disallowでブロックされているとnoindexを認識できない点を明示しています。今回は既存設定を維持し、インデックスされない保証とは報告しません。プレビューを非公開にする場合の認証設定は別途必要です。

## GitHub保存と作者情報

GitHub認証済みアカウントは `akirasauna-lab`、IDは317495863、作成日は2017年7月より後であることをAPIで確認。正しい形式のnoreplyを[GitHub公式仕様](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference)と照合し、リポジトリの `.git/config` だけに設定しました。

```text
user.name = akirasauna-lab
user.email = 317495863+akirasauna-lab@users.noreply.github.com
```

確認コマンド：`git config --show-origin --get-regexp '^user\.'`。グローバル設定は変更していません。push権限も確認済み。mainへはマージしません。

## 未確認・正式公開前の必須対応

1. Cloudflareアカウントは `wrangler whoami` で未認証。クラウド上のビルド・実デプロイ・カスタムドメイン・TLS・本番キャッシュは未確認。設定手順は `workers-publishing.md` を参照し、対象Workerとアカウントを確定して本番を検証すること。
2. 正式ドメイン、表示する運営者名、連絡先を確定して環境変数に入れること。コミット作者情報は運営者の公開連絡先の代用にはしない。
3. CloudflareのGit連携で本番ブランチがmain、作業ブランチは本番へ自動反映されないことを管理画面で確認すること。今回は管理画面設定を変更していない。
4. noindexを維持した公開準備版と、Google検索へ出す正式版の区別を決めること。現コードは検索公開用ではなく、sitemapの生成再開とnoindex/robotsの変更には別途承認・実装が必要。
5. 全記事は実機未検証。機種固有の操作を増やす場合は、型番・OS・手順の根拠を追加すること。実体験・改善率を創作しない。
6. 以前選んだ10テーマとの一致は今回も未確認。現在の13記事の確認と、この過去選定の照合は別事項。
7. AdSense・解析タグは未導入。導入時はプライバシーポリシーと広告配置を実態に合わせて改めること。

KURACALには変更を加えていません。外部本番公開・mainマージ・インデックス解除は行いません。
