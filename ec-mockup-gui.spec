# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec ファイル - EC Mockup GUI
生成コマンド: pyinstaller ec-mockup-gui.spec
出力先:      dist/ec-mockup-gui/
"""

import sys
from pathlib import Path

block_cipher = None

# プロジェクトルート
ROOT = Path(SPECPATH)

a = Analysis(
    [str(ROOT / "src" / "gui" / "app.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # .env.example と設定サンプルを同梱（.env 本体は同梱しない）
        (str(ROOT / ".env.example"), "."),
        (str(ROOT / "config" / "mock-site.yaml.example"), "config"),
    ],
    hiddenimports=[
        # click と関連モジュール
        "click",
        "dotenv",
        "yaml",
        "requests",
        "urllib3",
        # tkinter（Windows では通常同梱済みだが念のため）
        "tkinter",
        "tkinter.ttk",
        "tkinter.scrolledtext",
        "tkinter.messagebox",
        # src パッケージ全体
        "src.config.loader",
        "src.utils.logger",
        "src.utils.dirs",
        "src.fetchers.source_fetcher",
        "src.fetchers.data_exporter",
        "src.fetchers.image_fetcher",
        "src.fetchers.live_site_inspector",
        "src.builder.models",
        "src.builder.normalizer",
        "src.builder.renderer",
        "src.builder.static_builder",
        "src.usecase.runner",
        "src.gui.app",
        # Playwright は実行時インストールが必要なため除外
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "playwright",       # 実行時に別途インストール
        "pytest",
        "pytest_cov",
        "_pytest",
        "setuptools",
        "pip",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ec-mockup-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX は誤検知を起こしやすいため無効
    console=False,      # コンソールウィンドウを非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,          # アイコン未設定
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ec-mockup-gui",
)
