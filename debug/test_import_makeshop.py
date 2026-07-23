#!/usr/bin/env python
"""MakeshopClient インポートテスト"""
import sys
from pathlib import Path

print(f"Current directory: {Path.cwd()}")
print(f"__file__ would be in: {Path(__file__).parent if '__file__' in dir() else 'N/A'}")

# パス確認
ec_database_path = Path(__file__).parent.parent.parent.parent / "EC-database-tang" / "ec-database-tang"
print(f"EC-database-tang path: {ec_database_path}")
print(f"Path exists: {ec_database_path.exists()}")

# リストしてみる
if ec_database_path.exists():
    print(f"Contents of {ec_database_path}:")
    for item in ec_database_path.iterdir():
        print(f"  - {item.name}")

# sys.path に追加
sys.path.insert(0, str(ec_database_path))
print(f"\nsys.path[0]: {sys.path[0]}")

# インポート試行
try:
    from src.api.makeshop_client import client as makeshop_client
    print("✓ MakeshopClient import successful!")
    print(f"  client type: {type(makeshop_client)}")
    print(f"  client methods: {[m for m in dir(makeshop_client) if not m.startswith('_')][:10]}")
except Exception as e:
    print(f"✗ MakeshopClient import failed: {e}")
    import traceback
    traceback.print_exc()
