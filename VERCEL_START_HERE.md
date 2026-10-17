# 家電の解決ノート — GitHub と Vercel でプレビュー公開

## 作業前の確認
- `site/` に完成済みのHTMLが入っています。
- `vercel.json` はVercelで配信する場所を `site` に設定済みです。初期プレビューではビルド不要です。
- **この配布物はプレビュー用です。`noindex` と `robots.txt` によりGoogle検索には登録されません。** 本番用公開には別途 `SITE_URL`、`OPERATOR_NAME`、`CONTACT_EMAIL` を与えて `python build.py` で再生成してください。

## 公開手順
1. GitHubにログインし https://github.com/new から `kaden-kaiketsu-note` リポジトリを新規作成（KURACALとは別）。作成時、README自動生成はOFFでもOK。
2. 本ZIPをPC上で解凍。解凍先の `kaden-vercel-ready` の中身をGitHubの **Add file > Upload files** 画面にドラッグ&ドロップ。`vercel.json`、`site/`、`content/`、`build.py` がリポジトリの最上位にあるようにする。**ZIP本体をアップロードしても自動展開されません。**
3. Vercelの https://vercel.com/new から **Add New > Project**。GitHubを選び、新しいリポジトリを **Import**。
4. プロジェクト設定は **Framework Preset: Other**、**Root Directory: `./`**。`vercel.json` により Output Directory=`site`、Build Commandなし。もし設定画面で異なる値なら手動で変更。
5. **Deploy** を押す。完了したら表示された `*.vercel.app` でトップ、記事、検索を確認。

## 注意事項
- これは新規ドメインでの本番SEO公開とは別のプレビューです。
- 本番化にはドメイン取得、運営者情報・問い合わせメール確定、独自性の高い記事の検証、正規URLとsitemap生成、Search Console登録、AdSenseサイト審査が必要です。
- GitHubにパスワードやAPIキーなどをアップロードしないでください。
