#!/usr/bin/env python
"""MakeShop API から searchCategory でカテゴリ一覧を取得"""
import sys
sys.path.insert(0, 'd:/dev-programs/EC-database-tang/ec-database-tang')

from src.api.makeshop_client import client

# searchCategory でカテゴリ一覧を取得してみる
query = """
query {
    searchCategory {
        categories {
            categoryId
            categoryName
            categoryCode
            parentCategoryId
        }
    }
}
"""

try:
    result = client.execute_query(query)
    print("searchCategory 結果:")
    print(result)
except Exception as e:
    print(f"searchCategory エラー: {e}")
    print()
    
    # 別のクエリパターンを試す
    print("別のクエリパターンを試します...")
    query2 = """
    query {
        categories {
            id
            name
            code
        }
    }
    """
    try:
        result2 = client.execute_query(query2)
        print("categories 結果:")
        print(result2)
    except Exception as e2:
        print(f"categories エラー: {e2}")
