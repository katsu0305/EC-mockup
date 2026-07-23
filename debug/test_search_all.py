#!/usr/bin/env python
"""search_all_products_for_categories をテスト"""
import sys
sys.path.insert(0, 'd:/dev-programs/EC-database-tang/ec-database-tang')

from src.api.makeshop_client import client

try:
    print("全商品を取得中...")
    all_products = client.search_all_products_for_categories()
    print(f"取得商品数: {len(all_products)}")
    
    # カテゴリを集約
    all_categories = {}
    for product in all_products:
        categories = product.get("categories", [])
        for cat in categories:
            cat_name = cat.get("categoryName", "")
            if cat_name:
                all_categories[cat_name] = cat_name
    
    print(f"ユニークカテゴリ数: {len(all_categories)}")
    print("カテゴリ一覧:")
    for i, name in enumerate(sorted(all_categories.keys()), 1):
        print(f"  {i}. {name}")
        
except Exception as e:
    import traceback
    print(f"エラー: {e}")
    traceback.print_exc()
