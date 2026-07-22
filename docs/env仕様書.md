# .env 仕様書

## 1. 目的

本書は、ローカルモック生成ツールで使用する .env の正式なキー一覧、必須 / 任意区分、用途、設定例を定義する。

対象は以下の接続先と実行設定である。

- GitHub
- EC-database-tang API
- MakeShop 画像取得
- 実ショップサイト参照
- アプリケーション共通設定

機密情報は .env でローカル管理し、リポジトリには含めない。

---

## 2. 運用方針

### 2-1. 配置

- 開発時はプロジェクトルートに .env を配置する
- GUI 配布時は実行ファイルと同階層、または指定設定フォルダに .env を配置する

### 2-2. 管理ルール

- .env は Git 管理しない
- サンプル値は .env.example にのみ記載する
- パスワード、トークン、cookie をドキュメント本体に固定しない

### 2-3. 読み込み優先順位

1. OS 環境変数
2. .env
3. アプリのデフォルト値

---

## 3. キー一覧

### 3-1. GitHub 接続

| キー | 必須 | 型 | 用途 | 例 |
|---|---|---|---|---|
| GITHUB_TOKEN | 条件付き必須 | string | private repository 取得用 token | ghp_xxxxx |
| GITHUB_REPOSITORY | 必須 | string | 対象リポジトリ | your-org/ECsite |
| GITHUB_REF | 必須 | string | 取得対象 branch / tag / commit | main |
| GITHUB_SUBPATHS | 任意 | string | 取得対象パスのカンマ区切り | original,assets,お知らせ |

補足:

- public repository のみを扱う場合、GITHUB_TOKEN は省略可
- GITHUB_SUBPATHS 未指定時は設定ファイルの値を使う

### 3-2. EC-database-tang API 接続

| キー | 必須 | 型 | 用途 | 例 |
|---|---|---|---|---|
| ECDB_API_BASE_URL | 必須 | string | API ベース URL | http://127.0.0.1:8000/api/v1 |
| ECDB_API_KEY | 必須 | string | API キー | xxxxx |
| ECDB_API_TIMEOUT_SEC | 任意 | int | API タイムアウト秒 | 30 |
| ECDB_API_VERIFY_SSL | 任意 | bool | HTTPS 証明書検証 | true |

### 3-3. MakeShop 画像取得

| キー | 必須 | 型 | 用途 | 例 |
|---|---|---|---|---|
| MAKESHOP_PUBLIC_BASE_URL | 任意 | string | 公開画像ベース URL | https://gigaplus.makeshop.jp/groxidirect1 |
| MAKESHOP_FTP_HOST | 条件付き必須 | string | FTP ホスト | ftp-gigaplus.makeshop.jp |
| MAKESHOP_FTP_PORT | 任意 | int | FTP ポート | 21 |
| MAKESHOP_FTP_USER | 条件付き必須 | string | FTP ユーザー | groxidirect1 |
| MAKESHOP_FTP_PASSWORD | 条件付き必須 | string | FTP パスワード | xxxxx |
| MAKESHOP_FTP_PASSIVE | 任意 | bool | Passive モード | true |
| MAKESHOP_IMAGE_TIMEOUT_SEC | 任意 | int | ダウンロードタイムアウト秒 | 60 |
| MAKESHOP_IMAGE_RETRY_COUNT | 任意 | int | リトライ回数 | 3 |

補足:

- 公開 URL だけで十分な場合、FTP 系は省略可
- FTP 取得を有効化する場合、host / user / password は必須

### 3-4. 実ショップ参照

| キー | 必須 | 型 | 用途 | 例 |
|---|---|---|---|---|
| LIVE_SITE_BASE_URL | 必須 | string | 実ショップのベース URL | https://example-shop.example |
| LIVE_SITE_LOGIN_URL | 必須 | string | ログインページ URL | https://example-shop.example/login |
| LIVE_SITE_USERNAME | 条件付き必須 | string | ログイン ID | user@example.com |
| LIVE_SITE_PASSWORD | 条件付き必須 | string | ログインパスワード | xxxxx |
| LIVE_SITE_LOGIN_USER_FIELD | 任意 | string | ログイン ID 入力 name / selector | login_id |
| LIVE_SITE_LOGIN_PASSWORD_FIELD | 任意 | string | パスワード入力 name / selector | password |
| LIVE_SITE_LOGIN_SUBMIT_SELECTOR | 任意 | string | ログイン送信ボタン selector | button[type='submit'] |
| LIVE_SITE_LOGIN_SUCCESS_SELECTOR | 任意 | string | ログイン成功判定 selector | .header-menu |
| LIVE_SITE_COOKIE | 任意 | string | 手動投入 cookie | sessionid=xxxx |
| LIVE_SITE_USER_AGENT | 任意 | string | 取得時 User-Agent | Mozilla/5.0 ... |
| LIVE_SITE_EXTRA_HEADERS | 任意 | string(JSON) | 追加 HTTP ヘッダー | {"X-Test":"1"} |
| LIVE_SITE_HEADLESS | 任意 | bool | ブラウザを headless で起動するか | true |
| LIVE_SITE_WAIT_UNTIL | 任意 | string | ページ待機条件 | networkidle |
| LIVE_SITE_TIMEOUT_SEC | 任意 | int | ページ遷移タイムアウト秒 | 45 |
| LIVE_SITE_CAPTURE_CSS | 任意 | bool | CSS を保存するか | true |
| LIVE_SITE_CAPTURE_JS | 任意 | bool | JS を保存するか | true |
| LIVE_SITE_CAPTURE_SCREENSHOT | 任意 | bool | スクリーンショットを保存するか | true |

補足:

- ログイン方式が cookie 先行の場合、LIVE_SITE_COOKIE を優先使用してもよい
- ログインフォーム自動化が必要なため、初期実装はブラウザ自動化を前提とする

### 3-5. 出力 / 実行設定

| キー | 必須 | 型 | 用途 | 例 |
|---|---|---|---|---|
| APP_ENV | 任意 | string | 実行環境 | development |
| APP_LOG_LEVEL | 任意 | string | ログレベル | INFO |
| APP_WORK_DIR | 任意 | string | 作業ディレクトリ | ./work |
| APP_OUTPUT_DIR | 任意 | string | 出力ディレクトリ | ./output/mock-site |
| APP_TEMP_DIR | 任意 | string | 一時ディレクトリ | ./tmp |
| APP_CONFIG_FILE | 任意 | string | 設定ファイルパス | ./config/mock-site.yaml |

---

## 4. 必須最小セット

最小構成で必要な .env は以下。

```dotenv
GITHUB_REPOSITORY=your-org/ECsite
GITHUB_REF=main
GITHUB_TOKEN=

ECDB_API_BASE_URL=http://127.0.0.1:8000/api/v1
ECDB_API_KEY=replace-me

LIVE_SITE_BASE_URL=https://example-shop.example
LIVE_SITE_LOGIN_URL=https://example-shop.example/login
LIVE_SITE_USERNAME=replace-me
LIVE_SITE_PASSWORD=replace-me

MAKESHOP_PUBLIC_BASE_URL=https://gigaplus.makeshop.jp/your-shop-id
MAKESHOP_FTP_HOST=ftp-gigaplus.makeshop.jp
MAKESHOP_FTP_USER=replace-me
MAKESHOP_FTP_PASSWORD=replace-me

APP_LOG_LEVEL=INFO
APP_WORK_DIR=./work
APP_OUTPUT_DIR=./output/mock-site
```

---

## 5. 推奨 .env.example

```dotenv
# GitHub
GITHUB_REPOSITORY=your-org/ECsite
GITHUB_REF=main
GITHUB_SUBPATHS=original,assets,お知らせ
GITHUB_TOKEN=

# ECDB API
ECDB_API_BASE_URL=http://127.0.0.1:8000/api/v1
ECDB_API_KEY=
ECDB_API_TIMEOUT_SEC=30
ECDB_API_VERIFY_SSL=true

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

---

## 6. バリデーション仕様

### 6-1. 起動時必須チェック

- GITHUB_REPOSITORY が空でないこと
- GITHUB_REF が空でないこと
- ECDB_API_BASE_URL が URL 形式であること
- ECDB_API_KEY が空でないこと
- LIVE_SITE_BASE_URL が URL 形式であること
- LIVE_SITE_LOGIN_URL が URL 形式であること

### 6-2. 条件付きチェック

- LIVE_SITE_COOKIE 未設定なら LIVE_SITE_USERNAME と LIVE_SITE_PASSWORD を必須にする
- MAKESHOP_FTP_HOST を使う場合は MAKESHOP_FTP_USER と MAKESHOP_FTP_PASSWORD を必須にする
- LIVE_SITE_CAPTURE_CSS または LIVE_SITE_CAPTURE_JS が true の場合、保存先 work/live-site を自動作成する

### 6-3. 形式チェック

- bool は true / false のみ受理する
- int は 0 以上とする
- JSON 文字列はパース可能であること

---

## 7. セキュリティ方針

- パスワード、token、cookie はログ出力時にマスクする
- GUI 表示時は secret 値を伏せ字にする
- 例外発生時にも secret をそのまま例外文へ含めない
- .env.example にはダミー値または空文字のみを記載する

---

## 8. 将来拡張

- 複数ショップ切り替えのための prefix 対応
- 複数ログイン方式対応
- cookie ファイル読み込み対応
- GUI での secure storage 連携
