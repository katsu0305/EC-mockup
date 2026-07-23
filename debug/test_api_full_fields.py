#!/usr/bin/env python
"""MakeShop API searchProduct で取得できるフィールドをテスト"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.fetchers.makeshop_client_local import get_client

client = get_client()

# 詳細フィールドを追加してテスト
query = """
query searchProduct($input: SearchProductRequest!) {
    searchProduct(input: $input) {
        products {
            systemCode
            customCode
            productName
            productGroupCode
            productGroupName
            sellPrice
            consumerPrice
            taxRate
            quantity
            display
            maker
            janCode
            pcContent
            mobileContent
            pcAddContent
            mobileAddContent
            categories {
                categoryUID
                categoryName
                isMainCategory
            }
            createdAt
            updatedAt
        }
        searchedCount
        page
        limit
    }
}
"""

try:
    result = client.execute_query(query, {"input": {"page": 1, "limit": 2}})
    products = result.get("data", {}).get("searchProduct", {}).get("products", [])
    print(f"取得数: {len(products)}")
    if products:
        p = products[0]
        print(f"\n商品: {p.get('productName')}")
        print(f"  systemCode: {p.get('systemCode')}")
        print(f"  consumerPrice: {p.get('consumerPrice')}")
        print(f"  categories: {p.get('categories')}")
        print(f"  pcContent: {str(p.get('pcContent', ''))[:100]}")
        print(f"  pcAddContent: {str(p.get('pcAddContent', ''))[:100]}")
        print(f"  mobileContent: {str(p.get('mobileContent', ''))[:100]}")
        print(f"  mobileAddContent: {str(p.get('mobileAddContent', ''))[:100]}")
except Exception as e:
    import traceback
    print(f"エラー: {e}")
    traceback.print_exc()
