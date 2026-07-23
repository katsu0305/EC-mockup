# .env 仕様書

## 1. 目的

本書は、現行の ec-mockup 実装で利用する `.env` キーの用途、必須条件、設定例を定義する。

現在の主な接続先は以下。

- GitHub テンプレート取得
- MakeShop GraphQL API
- MakeShop 画像取得
- 実ショップ参照
- アプリケーション共通設定

`ECDB API` と `MSSQL` の設定はコード上に互換項目が残っているが、現在の標準フローでは使用しない。

## 2. 配置と読み込み

- 通常実行時: プロジェクトルートの `.env`
- PyInstaller 実行時: 実行ファイルと同階層の `.env`
- 優先順位: OS 環境変数 → `.env` → デフォルト値

## 3. キー一覧

### 3-1. GitHub

| キー | 必須条件 | 用途 |
|---|---|---|
| GITHUB_REPOSITORY | `fetch-source` / `build` 実行時に必須 | テンプレート取得元リポジトリ |
| GITHUB_REF | `fetch-source` / `build` 実行時に必須 | 取得対象 branch / tag / commit |
| GITHUB_SUBPATHS | 任意 | 抽出対象パス |
| GITHUB_TOKEN | private repository 時のみ必須 | GitHub API 認証 |

### 3-2. MakeShop API

| キー | 必須条件 | 用途 |
|---|---|---|
| MAKESHOP_API_ENDPOINT | 任意 | GraphQL エンドポイント |
| MAKESHOP_API_TOKEN | `export-data` / `build` 実行時に必須 | Bearer token |
| MAKESHOP_API_SECRET | `export-data` / `build` 実行時に必須 | HMAC 署名用 secret |
| MAKESHOP_API_KEY | 推奨 | `x-api-key` ヘッダー |

補足:

- `export-data` は MakeShop API から商品・価格・説明・カテゴリを取得する
- 公開中商品 (`display = Y`) のみ `products.json` に出力する

### 3-3. MakeShop 画像取得

| キー | 必須条件 | 用途 |
|---|---|---|
| MAKESHOP_PUBLIC_BASE_URL | 公開 URL 取得時に必須 | 公開画像ベース URL |
| MAKESHOP_FTP_HOST | `fetch-images --ftp` 時に必須 | FTP ホスト |
| MAKESHOP_FTP_PORT | 任意 | FTP ポート |
| MAKESHOP_FTP_USER | `fetch-images --ftp` 時に必須 | FTP ユーザー |
| MAKESHOP_FTP_PASSWORD | `fetch-images --ftp` 時に必須 | FTP パスワード |
| MAKESHOP_FTP_PASSIVE | 任意 | Passive モード |
| MAKESHOP_IMAGE_TIMEOUT_SEC | 任意 | ダウンロードタイムアウト |
| MAKESHOP_IMAGE_RETRY_COUNT | 任意 | リトライ回数 |

### 3-4. 実ショップ参照

| キー | 必須条件 | 用途 |
|---|---|---|
| LIVE_SITE_BASE_URL | `capture-live-site` 利用時に必須 | 実ショップベース URL |
| LIVE_SITE_LOGIN_URL | 任意 | ログインページ URL |
| LIVE_SITE_USERNAME | 条件付き | ログイン ID |
| LIVE_SITE_PASSWORD | 条件付き | ログインパスワード |
| LIVE_SITE_LOGIN_USER_FIELD | 任意 | ID 入力 selector / name |
| LIVE_SITE_LOGIN_PASSWORD_FIELD | 任意 | パスワード入力 selector / name |
| LIVE_SITE_LOGIN_SUBMIT_SELECTOR | 任意 | ログイン送信ボタン selector |
| LIVE_SITE_LOGIN_SUCCESS_SELECTOR | 任意 | ログイン成功判定 selector |
| LIVE_SITE_COOKIE | 任意 | 手動投入 cookie |
| LIVE_SITE_USER_AGENT | 任意 | User-Agent |
| LIVE_SITE_EXTRA_HEADERS | 任意 | JSON 形式追加ヘッダー |
| LIVE_SITE_HEADLESS | 任意 | headless 実行 |
| LIVE_SITE_WAIT_UNTIL | 任意 | ページ待機条件 |
| LIVE_SITE_TIMEOUT_SEC | 任意 | タイムアウト秒 |
| LIVE_SITE_CAPTURE_CSS | 任意 | CSS 保存 |
| LIVE_SITE_CAPTURE_JS | 任意 | JS 保存 |
| LIVE_SITE_CAPTURE_SCREENSHOT | 任意 | スクリーンショット保存 |

### 3-5. アプリ設定

| キー | 必須条件 | 用途 |
|---|---|---|
| APP_ENV | 任意 | 実行環境 |
| APP_LOG_LEVEL | 任意 | ログレベル |
| APP_WORK_DIR | 任意 | 作業ディレクトリ |
| APP_OUTPUT_DIR | 任意 | 出力ディレクトリ |
| APP_TEMP_DIR | 任意 | 一時ディレクトリ |
| APP_CONFIG_FILE | 任意 | YAML 設定ファイル |

## 4. 最小構成例

### 4-1. export-data / fetch-images 用

```dotenv
MAKESHOP_API_ENDPOINT=https://app-api.makeshop.jp/v1/graphql
MAKESHOP_API_TOKEN=replace-me
MAKESHOP_API_SECRET=replace-me
MAKESHOP_API_KEY=replace-me

MAKESHOP_PUBLIC_BASE_URL=https://gigaplus.makeshop.jp/your-shop-id
MAKESHOP_FTP_HOST=ftp-gigaplus.makeshop.jp
MAKESHOP_FTP_USER=replace-me
MAKESHOP_FTP_PASSWORD=replace-me

APP_LOG_LEVEL=INFO
APP_WORK_DIR=./work
APP_OUTPUT_DIR=./output/mock-site
```

### 4-2. build まで含む場合

```dotenv
GITHUB_REPOSITORY=your-org/ECsite
GITHUB_REF=main
GITHUB_SUBPATHS=original,assets,お知らせ

MAKESHOP_API_ENDPOINT=https://app-api.makeshop.jp/v1/graphql
MAKESHOP_API_TOKEN=replace-me
MAKESHOP_API_SECRET=replace-me
MAKESHOP_API_KEY=replace-me

MAKESHOP_PUBLIC_BASE_URL=https://gigaplus.makeshop.jp/your-shop-id
MAKESHOP_FTP_HOST=ftp-gigaplus.makeshop.jp
MAKESHOP_FTP_USER=replace-me
MAKESHOP_FTP_PASSWORD=replace-me
```

## 5. 現行 `.env.example`

```dotenv
# GitHub
GITHUB_REPOSITORY=your-org/ECsite
GITHUB_REF=main
GITHUB_SUBPATHS=original,assets,お知らせ
GITHUB_TOKEN=

# MakeShop API
MAKESHOP_API_ENDPOINT=https://app-api.makeshop.jp/v1/graphql
MAKESHOP_API_TOKEN=
MAKESHOP_API_SECRET=
MAKESHOP_API_KEY=

# MakeShop images
MAKESHOP_PUBLIC_BASE_URL=https://gigaplus.makeshop.jp/your-shop-id
MAKESHOP_FTP_HOST=ftp-gigaplus.makeshop.jp
MAKESHOP_FTP_PORT=21
MAKESHOP_FTP_USER=
MAKESHOP_FTP_PASSWORD=
MAKESHOP_FTP_PASSIVE=true
MAKESHOP_IMAGE_TIMEOUT_SEC=60
MAKESHOP_IMAGE_RETRY_COUNT=3

# Live site
LIVE_SITE_BASE_URL=https://example-shop.example
LIVE_SITE_LOGIN_URL=https://example-shop.example/login
LIVE_SITE_USERNAME=
LIVE_SITE_PASSWORD=
LIVE_SITE_LOGIN_USER_FIELD=login_id
LIVE_SITE_LOGIN_PASSWORD_FIELD=password
LIVE_SITE_LOGIN_SUBMIT_SELECTOR=button[type='submit']
LIVE_SITE_LOGIN_SUCCESS_SELECTOR=.header-menu
LIVE_SITE_COOKIE=
LIVE_SITE_USER_AGENT=
LIVE_SITE_EXTRA_HEADERS=
LIVE_SITE_HEADLESS=true
LIVE_SITE_WAIT_UNTIL=networkidle
LIVE_SITE_TIMEOUT_SEC=45
LIVE_SITE_CAPTURE_CSS=true
LIVE_SITE_CAPTURE_JS=true
LIVE_SITE_CAPTURE_SCREENSHOT=true

# App
APP_ENV=development
APP_LOG_LEVEL=INFO
APP_WORK_DIR=./work
APP_OUTPUT_DIR=./output/mock-site
APP_TEMP_DIR=./tmp
APP_CONFIG_FILE=./config/mock-site.yaml
```

## 6. セキュリティ方針

- `.env` は Git 管理しない
- token / secret / password / cookie をドキュメント本文へ固定しない
- ログ出力時に secret をそのまま出さない
- 配布時は `.env` を実行ファイルと別管理にするか、同階層に手動配置する
