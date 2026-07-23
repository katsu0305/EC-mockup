"""MakeShop API から商品データを取得して work/data へ保存する。"""
from __future__ import annotations

import json
from pathlib import Path

from src.config.loader import AppConfig
from src.fetchers.makeshop_client_local import get_client as get_makeshop_client
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.data_exporter")


def check_connection(cfg: AppConfig) -> bool:
    """MakeShop API の接続確認を行い、接続可否を返す。"""
    try:
        client = get_makeshop_client()
        result = client.execute_query("query { __typename }")
        ok = "__typename" in result.get("data", {})
        if ok:
            logger.info("MakeShop API 接続OK")
        else:
            logger.warning("MakeShop API レスポンス異常: %s", result)
        return ok
    except Exception as e:
        logger.error("MakeShop API 接続失敗: %s", e)
        return False


def export_data(cfg: AppConfig, latest_only: bool = True) -> Path:
    """
    MakeShop API から全商品を取得して work/data/products.json へ保存する。
    戻り値は保存ファイルのパス。
    """
    dest_dir = cfg.app_work_dir / "data"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "products.json"

    logger.info("MakeShop API から商品データ取得開始")

    client = get_makeshop_client()

    # 全商品を取得（pcContent, consumerPrice, categories 含む）
    api_products = client.search_all_products()

    # MakeShop API の camelCase → snake_case に変換して統一
    # display="Y"（公開中）の商品のみを対象とする
    all_items: list[dict] = []
    for p in api_products:
        if p.get("display") != "Y":
            continue
        # categories を変換（categoryUID → category_uid）
        raw_cats = p.get("categories") or []
        categories = [
            {
                "category_uid": str(c.get("categoryUID", "")),
                "category_name": c.get("categoryName", ""),
            }
            for c in raw_cats
            if c.get("categoryName")
        ]

        item = {
            "system_code": p.get("systemCode", ""),
            "custom_code": p.get("customCode", ""),
            "product_name": p.get("productName", ""),
            "product_group_code": p.get("productGroupCode", ""),
            "product_group_name": p.get("productGroupName", ""),
            "sell_price": p.get("sellPrice"),
            "consumer_price": p.get("consumerPrice"),
            "tax_rate": p.get("taxRate"),
            "quantity": p.get("quantity"),
            "display": p.get("display", ""),
            "maker": p.get("maker", ""),
            "jan_code": p.get("janCode", ""),
            "pc_content": p.get("pcContent", ""),
            "pc_add_content": p.get("pcAddContent", ""),
            "mobile_content": p.get("mobileContent", ""),
            "mobile_add_content": p.get("mobileAddContent", ""),
            "categories": categories,
            "makeshop_updated_at": p.get("updatedAt", ""),
        }
        all_items.append(item)

    total = len(all_items)
    logger.info("取得完了: %d 件", total)

    dest_file.write_text(
        json.dumps({"total": total, "items": all_items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("保存完了: %s (%d 件)", dest_file, total)

    # カテゴリマスタを取得
    categories_list = []
    try:
        product_categories = client.get_product_categories()
        for cat in product_categories:
            if cat.get("display") == "Y":
                categories_list.append({
                    "category_uid": str(cat.get("categoryUid", "")),
                    "category_name": cat.get("categoryName", ""),
                    "category_code": cat.get("categoryCode", ""),
                })
        logger.info("MakeShop API からカテゴリマスタ取得: %d件", len(categories_list))
    except Exception as e:
        logger.warning("MakeShop API カテゴリマスタ取得エラー: %s", e)
        # フォールバック：商品から集約
        seen: dict[str, str] = {}
        for item in all_items:
            for cat in item.get("categories", []):
                name = cat.get("category_name", "")
                if name and name not in seen:
                    seen[name] = name
        categories_list = [
            {"category_uid": str(i), "category_name": n}
            for i, n in enumerate(sorted(seen.values()), start=1)
        ]
        logger.info("商品から集約したカテゴリ: %d件", len(categories_list))

    categories_file = dest_file.parent / "categories.json"
    categories_file.write_text(
        json.dumps({"items": categories_list}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("カテゴリ保存完了: %s (%d 件)", categories_file, len(categories_list))

    return dest_file
