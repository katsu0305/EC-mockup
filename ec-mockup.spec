# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for ec-mockup CLI"""

block_cipher = None

a = Analysis(
    ['src/cli/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # テンプレートソース（MakeShop HTML テンプレート）
        ('work/source/original', 'work/source/original'),
        # assets（ロゴ・CSS・JS）
        ('work/source/assets', 'work/source/assets'),
    ],
    hiddenimports=[
        'src.cli.main',
        'src.cli.commands',
        'src.config.loader',
        'src.fetchers.data_exporter',
        'src.fetchers.makeshop_client_local',
        'src.fetchers.image_fetcher',
        'src.fetchers.source_fetcher',
        'src.builder.static_builder',
        'src.builder.renderer',
        'src.builder.normalizer',
        'src.builder.models',
        'src.utils.logger',
        'src.utils.dirs',
        'click',
        'dotenv',
        'requests',
        'yaml',
        'ftplib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pyodbc', 'playwright'],  # 不要な重いライブラリを除外
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
    name='ec-mockup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ec-mockup',
)
