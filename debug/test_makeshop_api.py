#!/usr/bin/env python
"""MakeShop API テスト"""
import sys
from pathlib import Path

# ec-mockup のパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from src.fetchers.makeshop_client_local import get_client

try:
    print("MakeShop API クライアントを初期化中...")
    client = get_client()
    print(f"Endpoint: {client.endpoint}")
    print(f"API Token: {client.api_token[:20]}..." if client.api_token else "API Token: NOT SET")
    print(f"API Secret: {client.api_secret[:20]}..." if client.api_secret else "API Secret: NOT SET")
    print()
    
    print("カテゴリマスタを取得中...")
    categories = client.get_product_categories()
    print(f"取得カテゴリ数: {len(categories)}")
    
    print("\nカテゴリ一覧（display=Y）:")
    for cat in categories:
        if cat.get("display") == "Y":
            print(f"  UID: {cat.get('categoryUid'):3} | Name: {cat.get('categoryName')}")
    
except Exception as e:
    import traceback
    print(f"エラー: {e}")
    traceback.print_exc()
