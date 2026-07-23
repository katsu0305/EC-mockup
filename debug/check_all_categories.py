#!/usr/bin/env python
"""MakeShop API から全商品のカテゴリを取得して集約"""
import sys
sys.path.insert(0, 'd:/dev-programs/EC-database-tang/ec-database-tang')

from src.api.makeshop_client import client
import json

all_categories = {}
product_count = 0
products_with_categories = 0

# すべてのページを取得
page = 1
while True:
    result = client.search_products(page=page, limit=50)
    products = result.get("products", [])
    
    if not products:
        break
    
    for product in products:
        product_count += 1
        categories = product.get("categories", [])
        
        if categories:
            products_with_categories += 1
            for cat in categories:
                # API は "categoryName" を返す
                cat_name = cat.get("categoryName", "")
                if cat_name:
                    all_categories[cat_name] = cat_name
    
    print(f"Page {page}: {len(products)} 件処理（カテゴリ発見: {len(all_categories)} ユニーク）")
    
    # searchedCount で総数を確認
    searched_count = result.get("searchedCount", 0)
    if searched_count <= page * 50:
        break
    
    page += 1

print(f"\n処理完了:")
print(f"  商品数: {product_count}")
print(f"  カテゴリ付き商品: {products_with_categories}")
print(f"  ユニークカテゴリ数: {len(all_categories)}")

if all_categories:
    print(f"\n発見されたカテゴリ:")
    for i, cat_name in enumerate(sorted(all_categories.keys()), start=1):
        print(f"  {i}. {cat_name}")
else:
    print("カテゴリ情報がまだ API から返されていません")
