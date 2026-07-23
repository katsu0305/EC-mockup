# 実装手順書 Phase 6 配布対応

## 1. 現在の方針

現行実装では CLI を PyInstaller で配布可能な形まで確認済み。GUI 配布は継続課題だが、CLI 実行ファイルの再現性は確保している。

## 2. 使用ファイル

- spec: [ec-mockup.spec](../ec-mockup.spec)
- 出力先: `dist/ec-mockup/`
- 実行ファイル: `dist/ec-mockup/ec-mockup.exe`

## 3. 同梱内容

PyInstaller で以下を同梱する。

- `src/cli/main.py` を起点とした CLI 本体
- `work/source/original` のテンプレート資産
- `work/source/assets` の静的 assets

同梱しないもの:

- `.env`
- `work/data`
- `work/images`
- `output/mock-site`
- MakeShop / GitHub の認証情報

## 4. ビルド手順

```powershell
pip install -e .[dev]
pyinstaller ec-mockup.spec --noconfirm
```

## 5. 配布構成

配布時は以下の構成を基本とする。

```text
dist/
	ec-mockup/
		ec-mockup.exe
		_internal/...
		.env                # 手動配置
```

`.env` は `ec-mockup.exe` と同じ階層に置く。

## 6. 動作確認済み項目

- `ec-mockup.exe --help`
- `ec-mockup.exe export-data`
- PyInstaller 実行時の `.env` 自動探索

## 7. 注意点

- `export-data` は MakeShop API 認証情報が必須
- `fetch-source` は GitHub 設定が必須
- `capture-live-site` を使う場合は Playwright のブラウザセットアップが別途必要
- `build` は画像を自動取得しないため、必要に応じて `fetch-images` を先に実行する

## 8. 今後の課題

- GUI 用 spec の整備
- 別マシンでの配布検証
- 初回セットアップ手順の簡略化
