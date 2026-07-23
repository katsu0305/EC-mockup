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

## 3. 現在の実装状況

現行実装は `capture-live-site` のサブコマンド構成を持つ。

- `run`: 実装済み
- `login-check`: 実装済み
- `diff`: 雛形のみ
- `clean`: 雛形のみ

## 4. 対象コマンド

### 4-1. メインコマンド

```text
ec-mockup capture-live-site run [OPTIONS]
```

### 4-2. 補助コマンド

```text
ec-mockup capture-live-site login-check [OPTIONS]
ec-mockup capture-live-site diff [OPTIONS]
ec-mockup capture-live-site clean [OPTIONS]
```

---

## 5. コマンド仕様

### 5-1. run

用途:

- 指定したページ群について、ログイン後の HTML / CSS / JS を取得して保存する

基本形:

```text
ec-mockup capture-live-site run --pages top,category,product
```

主なオプション:

| オプション | 内容 |
|---|---|
| --pages | 取得対象ページ種別。`top,category,product,news` のカンマ区切り |
| --headless / --no-headless | headless 実行切替 |
| --capture-screenshot | スクリーンショット保存 |
| --limit | 取得件数上限 |

成功時出力:

- 保存先ディレクトリ
- 取得ページ数
- 保存した CSS / JS 件数

終了コード:

- 0: 成功
- 1: 失敗

### 5-2. login-check

用途:

- .env の認証情報でクローズドサイトへログインできるかだけを検証する

基本形:

```text
ec-mockup capture-live-site login-check
```

成功条件:

- 成功判定 selector `.header-menu` が検出される

### 5-3. diff

用途:

- モックと実ショップの差分確認コマンドの入口

現状:

- 実装は TODO ログ出力のみ

### 5-4. clean

用途:

- `work/live-site` クリーンアップコマンドの入口

現状:

- 実装は TODO ログ出力のみ

---

## 6. 取得フロー

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

## 7. 保存構造

```text
work/
  live-site/
    top/
      index.html
      css/
      js/
      screenshot.png
    shop/
      index.html
      css/
      js/
    info/
      index.html
      css/
      js/
```

補足:

- ルートパス `/` は `top` というディレクトリ名で保存される
- そのほかは URL パスを slug 化したディレクトリ名になる


## 8. .env 依存キー

本 CLI が主に使用する .env キーは以下。

- LIVE_SITE_BASE_URL
- LIVE_SITE_LOGIN_URL
- LIVE_SITE_USERNAME
- LIVE_SITE_PASSWORD
- コード上では selector は固定値を使用している
- LIVE_SITE_HEADLESS
- LIVE_SITE_TIMEOUT_SEC

固定 selector:

- `[name='login_id']`
- `[name='password']`
- `button[type='submit']`
- `.header-menu`


## 9. 取得対象ページの決め方

### 8-1. ページ種別指定

- top: トップページ 1 件
- category: サンプルカテゴリページ複数件
- product: URL 文字列として解決される追加指定用
- news: お知らせ一覧と詳細

### 9-2. 既定パス

- top: `/`
- category: `/shop/`
- news: `/info/`

## 10. 注意点

- 実ショップ取得物を生成の正本へ昇格させない
- Playwright のブラウザセットアップが必要
- `diff` と `clean` は現時点では未完成コマンド

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
