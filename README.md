# 家電の解決ノート（仮） — 新規Webサイト

家電の「つながらない」「映らない」「反応しない」を、公式サポートの参照先とともに順番に確認できる、広告収益を目指す独立サイトの初期版です。KURACALには変更を加えていません。

## 作成済み

- トップページ（検索欄、カテゴリ4種、ガイド一覧、キーワード/カテゴリ絞り込み）
- 10記事（Fire TV / Chromecast / SwitchBot / iPhone / Windows）
- 記事ごとの参照先、FAQ、関連コンテンツ、閲覧用のステップ
- スマホ対応、各ページのtitle/description、OG用SVG、JSON-LD構造化データ
- このサイトについて、編集方針、プライバシーポリシー
- 広告タグやアクセス解析タグは未挿入（審査前の状態）

## まずはプレビューする

`site/` 内が配信用の完成済み静的サイトです。相対リンクを正しく確認するにはブラウザで `index.html` を直接開かず、ローカルWebサーバーを使用してください。

```bash
cd site
python -m http.server 8000
```

ブラウザで `http://localhost:8000` を開きます。

## 記事を編集・追加する

`content/articles.json` が記事の元データです。記事を変更後、以下を実行すると全ページを作り直せます。

```bash
python -m pip install jinja2
python build.py
```

外観は `site/assets/styles.css`、検索やカテゴリの動作は `site/assets/main.js` で調整できます。`build.py` は静的HTMLを生成するスクリプトで、npmやNode.jsは不要です。

## 公開する手順（おすすめ：Netlify / Cloudflare Pages）

1. 先に独自ドメインを決めて取得する（このZIPにはドメインを含めていません）。
2. 公開前に `/about/` の運営者情報、`/privacy/` の問い合わせ先・実際の解析/広告仕様を更新する。
3. ドメインを含むcanonicalとsitemapを生成する。

   ```bash
   SITE_URL=https://あなたのドメイン python build.py
   ```

4. `site/` フォルダの中身をNetlifyの手動デプロイ、またはCloudflare PagesのDirect Uploadへアップロード。公開ルートが `site/index.html` になるようにする。
5. Google Search Consoleに新サイトを登録し、`https://あなたのドメイン/sitemap.xml` を送信する。
6. 実際の機種を使った検証・画面写真などの独自情報を追加し、公開ページを確認する。
7. 公開済みの内容とポリシーを整えたうえで、Google AdSenseに新しいサイトとして申請する。承認後に広告コードを実装する。**AdSenseの承認や検索上位表示は保証されません。**

現時点ではサイトをインターネット上に公開していません。ドメイン取得・登録・AdSense申請も未実施です。

## 収益検証の基準

最初の目標は **月間1万円（売上ベース）**。例えば実測ページRPM 400円なら月25,000PVが必要ですが、これは仮定であり達成予測ではありません。Search Consoleで検索表示数・クリック・検索順位を確認し、AdSense承認後はページRPMを実測してください。

## 安全と編集上の注意

- 情報はメーカー公式サポートなどを確認し、各記事に参照先URLを記載しています。
- **実機テストを全機器で実施したわけではありません。**実機検証済みのような表現はしないでください。
- 型番・OS・サポート情報の更新で内容が変わるため、公開直前と更新時に再確認してください。
- 異臭・発熱・破損・感電のおそれなどがあれば使用を中止し、メーカーや専門業者へ相談するよう案内してください。
- 広告を挿入する場合は、記事リンクや操作ボタンと紛らわしい配置を避け、AdSenseポリシーを確認してください。
- サイト名は仮称であり、商標・ドメインの利用可否は取得前に別途確認してください。

## プロジェクト構成

```text
kaden-kaiketsu-note/
├── README.md
├── build.py
├── content/
│   └── articles.json
└── site/                 # 配信するフォルダ
    ├── index.html
    ├── assets/
    ├── category/
    ├── articles/
    ├── about/
    ├── editorial/
    ├── privacy/
    ├── 404.html
    └── robots.txt
```

## 2026年10月 継続作業版

- 記事10本すべてに「試した手順」チェックボックス、進捗ゲージ、結果コピー、リセットを追加。
- チェック状況はブラウザのローカルストレージに保存され、外部サーバーには送信されません。
- URL未確定のプレビュー版は `noindex,nofollow`・`robots.txt Disallow: /` で誤インデックスを防止。
- **本番版には** `SITE_URL` に加えて `OPERATOR_NAME` と `CONTACT_EMAIL` が必須です。これらを省いた状態では本番用のビルドを生成できません。
- `tests/site_check.py` は内部リンク・見出し・メタデータなどを検査。`tests/browser_check.py` はブラウザ内の検索・チェックリスト・モバイル表示などを検査。
- 公開前の作業手順は **[PUBLISHING_GUIDE.md](PUBLISHING_GUIDE.md)** を参照。
