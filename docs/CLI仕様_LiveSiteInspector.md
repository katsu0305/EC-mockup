# CLI仕様書 Live Site Inspector

## 1. 目的

本書は、実ショップサイトから HTML / CSS / JS を取得し、比較用スナップショットとして保存する Live Site Inspector の CLI 仕様を定義する。

Live Site Inspector は生成の正本ではなく、以下の補助用途に限定して使う。

- 実ショップの DOM 構造確認
- 適用 CSS / JS の確認
- ローカルモックとの見た目差分確認
- レンダラ調整時の参照資料取得

---

## 2. 基本方針

- クローズドサイト前提でログイン後のページを取得する
- HTML だけでなく、参照される CSS / JS も保存する
- 認証情報は .env から読む
- 初期実装は Playwright ベースのブラウザ自動化を第一候補とする
- 取得物は work/live-site 配下へ保存する

---

## 3. 対象コマンド

### 3-1. メインコマンド

```text
ec-mockup capture-live-site [OPTIONS]
```

### 3-2. 補助コマンド

```text
ec-mockup capture-live-site login-check [OPTIONS]
ec-mockup capture-live-site diff [OPTIONS]
ec-mockup capture-live-site clean [OPTIONS]
```

---

## 4. コマンド仕様

### 4-1. capture-live-site

用途:

- 指定したページ群について、ログイン後の HTML / CSS / JS を取得して保存する

基本形:

```text
ec-mockup capture-live-site --pages top,category,product
```

主なオプション:

| オプション | 必須 | 内容 |
|---|---|---|
| --pages | 任意 | 取得対象ページ種別。top, category, product, news |
| --urls-file | 任意 | 個別 URL 一覧ファイル |
| --output-dir | 任意 | 保存先。未指定時は work/live-site |
| --headless / --no-headless | 任意 | headless 実行切替 |
| --capture-css / --no-capture-css | 任意 | CSS 保存有無 |
| --capture-js / --no-capture-js | 任意 | JS 保存有無 |
| --capture-screenshot | 任意 | スクリーンショット保存 |
| --wait-until | 任意 | load, domcontentloaded, networkidle |
| --timeout | 任意 | タイムアウト秒 |
| --limit | 任意 | 取得件数上限 |
| --force-login | 任意 | cookie があってもログイン処理を再実行 |
| --save-session | 任意 | cookie / storage state を保存 |

成功時出力:

- 保存先ディレクトリ
- 取得ページ数
- 保存した CSS / JS 件数
- 失敗 URL 一覧

終了コード:

- 0: 全件成功
- 1: 一部失敗
- 2: ログイン失敗
- 3: 設定不備

### 4-2. login-check

用途:

- .env の認証情報でクローズドサイトへログインできるかだけを検証する

基本形:

```text
ec-mockup capture-live-site login-check
```

成功条件:

- 指定した成功判定 selector が検出される
- ログイン後の base URL 配下へ遷移できる

終了コード:

- 0: 成功
- 2: 認証失敗
- 3: 設定不備

### 4-3. diff

用途:

- 取得済み実ショップスナップショットと output/mock-site の HTML を比較する

基本形:

```text
ec-mockup capture-live-site diff --page product --live work/live-site/product --mock output/mock-site/products/ABC123
```

初期比較対象:

- title
- 主要見出し
- 商品名
- 価格表示ブロック
- パンくず
- 画像数
- 読み込まれている CSS / JS の差分サマリ

### 4-4. clean

用途:

- work/live-site 配下の取得物を削除する

基本形:

```text
ec-mockup capture-live-site clean --yes
```

---

## 5. 取得フロー

### 5-1. 標準フロー

1. .env を読み込む
2. 必須キーをバリデーションする
3. ブラウザを起動する
4. ログインページへ遷移する
5. ID / パスワードを入力する、または cookie を適用する
6. ログイン成功を確認する
7. 対象ページへ順に遷移する
8. レンダリング後 HTML を保存する
9. 読み込まれている CSS / JS を収集して保存する
10. 必要に応じてスクリーンショットを保存する
11. サマリを出力して終了する

### 5-2. フォールバック

- cookie ログインが有効ならフォームログインを省略してよい
- JS を伴わない単純ページ取得だけなら HTTP クライアント取得を補助的に使ってよい
- ただし標準実装はブラウザ自動化とする

---

## 6. 保存構造

```text
work/
  live-site/
    session/
      storage-state.json
      cookies.json
    top/
      page.html
      screenshot.png
      css/
        main.css
        vendor-01.css
      js/
        app.js
        vendor-01.js
      meta.json
    category/
      category-001/
        page.html
        screenshot.png
        css/
        js/
        meta.json
    product/
      BM-MNLBP01NBK/
        page.html
        screenshot.png
        css/
        js/
        meta.json
```

meta.json に保存する項目:

- requested_url
- final_url
- captured_at
- login_method
- css_files
- js_files
- screenshot_path
- page_type
- system_code or page_key

---

## 7. .env 依存キー

本 CLI が主に使用する .env キーは以下。

- LIVE_SITE_BASE_URL
- LIVE_SITE_LOGIN_URL
- LIVE_SITE_USERNAME
- LIVE_SITE_PASSWORD
- LIVE_SITE_LOGIN_USER_FIELD
- LIVE_SITE_LOGIN_PASSWORD_FIELD
- LIVE_SITE_LOGIN_SUBMIT_SELECTOR
- LIVE_SITE_LOGIN_SUCCESS_SELECTOR
- LIVE_SITE_COOKIE
- LIVE_SITE_USER_AGENT
- LIVE_SITE_EXTRA_HEADERS
- LIVE_SITE_HEADLESS
- LIVE_SITE_WAIT_UNTIL
- LIVE_SITE_TIMEOUT_SEC
- LIVE_SITE_CAPTURE_CSS
- LIVE_SITE_CAPTURE_JS
- LIVE_SITE_CAPTURE_SCREENSHOT

---

## 8. 取得対象ページの決め方

### 8-1. ページ種別指定

- top: トップページ 1 件
- category: サンプルカテゴリページ複数件
- product: サンプル商品詳細ページ複数件
- news: お知らせ一覧と詳細

### 8-2. URL 解決方法

優先順位:

1. --urls-file 指定
2. 設定ファイルのサンプル URL 一覧
3. 生成済み商品データから導出

---

## 9. ログ仕様

最低限出すログ:

- .env 読み込み開始 / 完了
- ログイン開始 / 成功 / 失敗
- 各 URL の取得開始 / 完了 / 失敗
- CSS / JS 保存件数
- スクリーンショット保存結果
- 合計件数と失敗件数

secret 値はマスクする。

---

## 10. 失敗時の扱い

### 10-1. ログイン失敗

- 即時中断
- 終了コード 2
- selector 不一致、認証エラー、タイムアウトを切り分けて出す

### 10-2. 一部ページ失敗

- 失敗ページを記録して継続
- 終了コード 1

### 10-3. CSS / JS 個別失敗

- HTML 保存は継続
- 欠損ファイル一覧を meta.json とログに残す

---

## 11. 初期実装の技術方針

- CLI フレームワーク: Typer
- ブラウザ自動化: Playwright for Python
- HTML 解析補助: BeautifulSoup または lxml
- ログ: 標準 logging
- .env 読み込み: python-dotenv または pydantic-settings

Playwright を第一候補にする理由:

- ログインフォーム操作がしやすい
- JS 実行後 DOM を取りやすい
- CSS / JS リクエストの把握がしやすい
- スクリーンショットも同時に保存しやすい

---

## 12. 非対象

- 全ページ自動巡回による完全サイトクロール
- 実ショップ HTML をそのままビルド元にする処理
- クローズドサイトのセキュリティ回避を目的とする実装

---

## 13. 受け入れ基準

- login-check でログイン可否を確認できる
- capture-live-site で HTML / CSS / JS が保存される
- 保存結果が work/live-site 配下で追跡できる
- diff でローカル生成物との差分確認ができる
- secret 値がログへ露出しない
