#!/usr/bin/env python
"""MakeShop API の getProductCategory をテスト"""
import sys
sys.path.insert(0, 'd:/dev-programs/EC-database-tang/ec-database-tang')

from src.api.makeshop_client import client

# パターン1: 第1階層のみ
try:
    print("パターン1: depth=1 でクエリ...")
    result = client.get_product_categories(depth=1)
    print(f"結果: {result}")
except Exception as e:
    print(f"エラー: {e}")

print("\n---\n")

# パターン2: GraphQL クエリを直接実行
try:
    print("パターン2: GraphQL クエリ直接実行...")
    query = """
    query {
        getProductCategory {
            categoryUID
            categoryName
            categoryDepth
        }
    }
    """
    result = client.execute_query(query)
    print(f"結果: {result}")
except Exception as e:
    print(f"エラー: {e}")

print("\n---\n")

# パターン3: searchProduct で categories を確認
try:
    print("パターン3: searchProduct で categories を確認...")
    result = client.search_products(page=1, limit=5)
    products = result.get("products", [])
    print(f"最初の商品: {products[0] if products else 'なし'}")
except Exception as e:
    print(f"エラー: {e}")
