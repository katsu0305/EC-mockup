#!/usr/bin/env python
"""MakeShop API の getProductCategory クエリをテスト"""
import sys
sys.path.insert(0, 'd:/dev-programs/EC-database-tang/ec-database-tang')

from src.api.makeshop_client import client

try:
    print("getProductCategory クエリ実行中...")
    categories = client.get_product_categories()
    print(f"取得カテゴリ数: {len(categories)}")
    
    print("\nカテゴリ一覧（第1階層、display=Y）:")
    for cat in categories:
        if cat.get("display") == "Y":
            print(f"  UID: {cat.get('categoryUid'):3} | Code: {cat.get('categoryCode'):20} | Name: {cat.get('categoryName')}")
    
    print(f"\n合計表示カテゴリ: {len([c for c in categories if c.get('display') == 'Y'])}")
        
except Exception as e:
    import traceback
    print(f"エラー: {e}")
    traceback.print_exc()
