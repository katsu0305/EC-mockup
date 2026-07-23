"""MakeShop API クライアント（簡易版）"""
from typing import Any, Dict, Optional, List
import requests
import hmac
import hashlib
import time
from src.utils.logger import get_logger
import os
from pathlib import Path
from dotenv import load_dotenv

logger = get_logger("ec_mockup.makeshop_client")


def _find_env_path() -> Path:
    """PyInstaller バンドルと通常実行の両方に対応した .env パス解決。"""
    import sys
    # PyInstaller バンドルの場合： sys.executable の親ディレクトリ
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        # 通常実行：プロジェクトルート（src/fetchers/ から 3 階層上）
        base = Path(__file__).parent.parent.parent
    return base / ".env"


_env_path = _find_env_path()
load_dotenv(dotenv_path=_env_path)


class MakeshopAPIClient:
    """MakeShop GraphQL API クライアント"""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_token: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.endpoint = endpoint or os.getenv("MAKESHOP_API_ENDPOINT", "https://app-api.makeshop.jp/v1/graphql")
        self.api_token = api_token or os.getenv("MAKESHOP_API_TOKEN", "")
        self.api_secret = api_secret or os.getenv("MAKESHOP_API_SECRET", "")
        self.api_key = api_key or os.getenv("MAKESHOP_API_KEY", "")
        
        if not self.api_token:
            logger.warning("MAKESHOP_API_TOKEN not set (.env の MAKESHOP_API_TOKEN を確認してください)")
        if not self.api_secret:
            logger.warning("MAKESHOP_API_SECRET not set (.env の MAKESHOP_API_SECRET を確認してください)")
    
    def _generate_signature(self, timestamp: str) -> str:
        """HMAC-SHA256 署名を生成"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            timestamp.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_headers(self) -> Dict[str, str]:
        """認証ヘッダーを生成"""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_token and self.api_secret:
            timestamp = str(int(time.time()))
            signature = self._generate_signature(timestamp)
            headers["Authorization"] = f"Bearer {self.api_token}"
            headers["x-timestamp"] = timestamp
            headers["x-signature"] = signature
            if self.api_key:
                headers["x-api-key"] = self.api_key
        
        return headers
    
    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GraphQL クエリを実行"""
        headers = self._get_headers()
        
        payload = {
            "query": query,
        }
        if variables:
            payload["variables"] = variables
        
        try:
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            
            if "errors" in result:
                error_msg = result["errors"][0].get("message", "Unknown GraphQL error")
                logger.error(f"GraphQL API error: {error_msg}")
                raise Exception(f"GraphQL error: {error_msg}")
            
            return result
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_product_categories(self) -> List[Dict[str, Any]]:
        """カテゴリマスタを取得"""
        query = """
        query getProductCategory {
          getProductCategory {
            productCategories {
              categoryUid
              categoryCode
              categoryName
              display
              productSortType
              memberAccessType
              memberGroupIds
              categoryDepth
              category1
              category2
              category3
              category4
              category5
              categoryUrl
              addCategoryUrl
              seoInfo {
                browserTitle
                description
              }
            }
          }
        }
        """
        
        result = self.execute_query(query)
        product_categories = result.get("data", {}).get("getProductCategory", {}).get("productCategories", [])
        return product_categories if isinstance(product_categories, list) else []

    def search_all_products(self) -> List[Dict[str, Any]]:
        """全商品を取得（全フィールド含む）
        
        Returns:
            全商品データのリスト
        """
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
        
        all_products = []
        page = 1
        
        while True:
            variables = {"input": {"page": page, "limit": 50}}
            result = self.execute_query(query, variables)
            data = result.get("data", {}).get("searchProduct", {})
            products = data.get("products", [])
            
            if not products:
                break
            
            all_products.extend(products)
            
            searched_count = data.get("searchedCount", 0)
            if len(all_products) >= searched_count:
                break
            
            page += 1
        
        logger.info("MakeShop API から全商品取得: %d件", len(all_products))
        return all_products


# グローバルインスタンス
_client = None


def get_client() -> MakeshopAPIClient:
    """MakeShop API クライアントのシングルトンを取得"""
    global _client
    if _client is None:
        _client = MakeshopAPIClient()
    return _client
