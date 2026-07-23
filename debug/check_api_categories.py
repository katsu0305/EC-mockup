#!/usr/bin/env python
"""MakeShop API から categories データ取得確認"""
import sys
sys.path.insert(0, 'd:/dev-programs/EC-database-tang/ec-database-tang')

from src.api.makeshop_client import client

# 最初の 3 ページを取得して categories を確認
print("MakeShop API から category 情報を取得中...\n")

all_categories = {}
for page in range(1, 4):
    result = client.search_products(page=page, limit=50)
    products = result.get("products", [])
    
    print(f"--- Page {page} ({len(products)} 件) ---")
    
    for product in products[:3]:  # 最初の 3 件表示
        system_code = product.get("systemCode")
        product_name = product.get("productName", "")[:30]
        categories = product.get("categories", [])
        
        print(f"{system_code}: {product_name}")
        print(f"  categories: {categories}")
        
        # 全カテゴリを収集
        if categories:
            for cat in categories:
                cat_name = cat.get("categoryName", "")
                if cat_name:
                    all_categories[cat_name] = cat_name
    
    print()

print(f"\n全ユニークなカテゴリ ({len(all_categories)} 件):")
for cat_name in sorted(all_categories.keys()):
    print(f"  - {cat_name}")
