# 実装手順書 Phase 2 入力取得機能実装

## 1. 目的

GitHub、EC-database-tang、MakeShop 画像、実ショップ参照の 4 系統から必要データを取得できるようにする。

## 2. 開始条件

- Phase 1 が完了していること
- .env が最小セットで埋まっていること

## 3. 実施手順

### 3-1. GitHub 取得を実装する

1. リポジトリ指定を受け取る
2. ref 指定を受け取る
3. 対象 subpaths のみ取得する
4. work/source 配下へ展開する

### 3-2. 商品データ取得を実装する

1. ECDB API の接続確認を行う
2. 商品一覧取得を実装する
3. ページネーション対応を入れる
4. 中間 JSON を保存する

### 3-3. 画像取得を実装する

1. 商品データとテンプレートから画像参照を抽出する
2. 公開 URL ダウンロードを実装する
3. FTP ダウンロードを実装する
4. 重複排除を入れる
5. タイムアウトとリトライを入れる

### 3-4. Live Site Inspector を実装する

1. .env を使ったログイン処理を実装する
2. login-check を実装する
3. HTML 取得を実装する
4. CSS 取得を実装する
5. JS 取得を実装する
6. meta.json と screenshot 保存を実装する

### 3-5. 取得結果の保存構造を固定する

1. work/source を整える
2. work/live-site を整える
3. work/data を整える
4. work/images を整える

## 4. 成果物

- 取得済みテンプレート
- 商品 JSON
- ローカル画像群
- 実ショップ HTML/CSS/JS スナップショット

## 5. 完了判定

- fetch-source が成功する
- export-data が成功する
- fetch-images が成功する
- capture-live-site login-check が成功する
- capture-live-site で HTML/CSS/JS が保存される

## 6. 注意点

- 実ショップ取得物を正本へ昇格させない
- 画像を全件同期しない
- 認証情報をログへ出さない
