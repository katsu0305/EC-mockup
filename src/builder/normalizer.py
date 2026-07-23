"""ECDB API の products.json を内部モデルへ変換する。"""
from __future__ import annotations

import json
from pathlib import Path

from src.builder.models import (
    Category,
    CategorySummary,
    ProductCard,
    ProductDetail,
    SiteContext,
    Variation,
)
from src.config.loader import AppConfig
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.normalizer")


def load_site_context(cfg: AppConfig) -> SiteContext:
    """
    work/data/products.json と categories.json から SiteContext を構築する。
    ファイルが存在しない場合はデモデータで代替する。
    """
    products_file = cfg.app_work_dir / "data" / "products.json"
    if products_file.exists():
        raw = json.loads(products_file.read_text(encoding="utf-8"))
        items = raw.get("items", [])
        logger.info("products.json 読み込み: %d 件", len(items))
    else:
        logger.warning("products.json が見つかりません。デモデータを使用します: %s", products_file)
        items = _demo_items()

    # categories.json を読み込み
    categories_file = cfg.app_work_dir / "data" / "categories.json"
    categories_list: list[CategorySummary] = []
    if categories_file.exists():
        try:
            raw_cat = json.loads(categories_file.read_text(encoding="utf-8"))
            cat_items = raw_cat.get("items", [])
            logger.info("categories.json 読み込み: %d 件", len(cat_items))
            
            # 辞書リストを CategorySummary に変換
            for cat in cat_items:
                cat_name = cat.get("category_name", "")
                cat_uid = cat.get("category_uid", "")
                categories_list.append(
                    CategorySummary(
                        name=cat_name,
                        url=f"category/{cat_uid}.html" if cat_uid else "#",
                    )
                )
        except Exception as e:
            logger.error("categories.json 読み込みエラー: %s", e)
    else:
        logger.warning("categories.json が見つかりません: %s", categories_file)

    details = [_to_detail(item, cfg) for item in items]

    return SiteContext(
        shop_name="ELECOM 4 YOU",
        logo_url="assets/images/brand/logo/logo.png",
        products=details,
        categories=categories_list,
    )


# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _to_detail(item: dict, cfg: AppConfig) -> ProductDetail:
    code = item.get("system_code", "")
    custom_code = item.get("custom_code", "")
    sell_price = item.get("sell_price") or 0
    consumer_price = item.get("consumer_price") or sell_price

    image_url = _resolve_image_url(code, cfg, custom_code)

    variations_raw = item.get("variations") or []
    variations = [
        Variation(
            variation_id=v.get("variation_id", 0),
            name1=v.get("variation1_value", ""),
            name2=v.get("variation2_value", ""),
            quantity=v.get("quantity", 0),
            is_soldout=(v.get("quantity", 0) == 0),
        )
        for v in variations_raw
    ]

    categories_raw = item.get("categories") or []
    categories = [
        Category(
            category_uid=c.get("category_uid", ""),
            category_name=c.get("category_name", "")
        )
        for c in categories_raw
        if c.get("category_name")
    ]

    return ProductDetail(
        system_code=code,
        custom_code=item.get("custom_code", ""),
        name=item.get("product_name", ""),
        sell_price=sell_price,
        consumer_price=consumer_price,
        tax_rate=float(item.get("tax_rate") or 0.1),
        quantity=item.get("quantity", 0),
        image_url=image_url,
        detail_url=f"products/{code}.html",
        is_soldout=(item.get("quantity", 0) == 0),
        is_sale=(consumer_price > sell_price > 0),
        is_member_only=(item.get("is_member_only") == "Y"),
        variations=variations,
        categories=categories,
        description=item.get("pc_content", ""),
        add_content=item.get("pc_add_content", ""),
    )


def _resolve_image_url(system_code: str, cfg: AppConfig, custom_code: str = "") -> str:
    """ローカル画像があればそちらを使い、なければ公開 URL を返す。
    
    優先順位：
    1. work/images/img/{custom_code}/ 配下の最初の画像
    2. 公開 URL
    
    戻り値は depth なしの相対パス（renderer で _root_path() 経由で補正される）
    """
    # custom_code ベースで探す
    if custom_code:
        img_dir = cfg.app_work_dir / "images" / "img" / custom_code
        if img_dir.exists():
            # ディレクトリ内の画像ファイルを探す
            for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                for img_file in img_dir.glob(f"*{ext}"):
                    rel = f"work/images/img/{custom_code}/{img_file.name}"
                    return rel
    
    # フォールバック：公開 URL
    if cfg.makeshop_public_base_url:
        return f"{cfg.makeshop_public_base_url.rstrip('/')}/img/{custom_code}/main.jpg"
    return "assets/images/no-image.png"


def _build_categories(products: list[ProductDetail]) -> list[CategorySummary]:
    """商品データからカテゴリ一覧を構築する。"""
    cat_map: dict[str, CategorySummary] = {}
    for p in products:
        for cat_name in p.categories:
            if cat_name not in cat_map:
                slug = cat_name.replace(" ", "_").replace("/", "_")
                cat_map[cat_name] = CategorySummary(
                    name=cat_name,
                    url=f"categories/{slug}.html",
                )
            card = ProductCard(
                system_code=p.system_code,
                name=p.name,
                sell_price=p.sell_price,
                consumer_price=p.consumer_price,
                image_url=p.image_url,
                detail_url=p.detail_url,
                is_soldout=p.is_soldout,
                is_sale=p.is_sale,
                category_name=cat_name,
                category_url=cat_map[cat_name].url,
            )
            cat_map[cat_name].products.append(card)
    return list(cat_map.values())


def _demo_items() -> list[dict]:
    """API 未接続時に使うデモ商品データ。"""
    return [
        {
            "system_code": "DEMO-001",
            "custom_code": "DEMO-001",
            "product_name": "【デモ】エレコム ゲーミングマウス",
            "sell_price": 3980,
            "consumer_price": 4980,
            "tax_rate": 0.1,
            "quantity": 10,
            "is_member_only": "N",
            "categories": [{"category_name": "マウス"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-002",
            "custom_code": "DEMO-002",
            "product_name": "【デモ】エレコム USB ハブ 4ポート",
            "sell_price": 1980,
            "consumer_price": 1980,
            "tax_rate": 0.1,
            "quantity": 0,
            "is_member_only": "N",
            "categories": [{"category_name": "USBハブ"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-003",
            "custom_code": "DEMO-003",
            "product_name": "【デモ】エレコム ワイヤレスキーボード",
            "sell_price": 2980,
            "consumer_price": 3280,
            "tax_rate": 0.1,
            "quantity": 5,
            "is_member_only": "N",
            "categories": [{"category_name": "キーボード"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-004",
            "custom_code": "DEMO-004",
            "product_name": "【デモ】エレコム USB-C ケーブル 2m",
            "sell_price": 980,
            "consumer_price": 980,
            "tax_rate": 0.1,
            "quantity": 25,
            "is_member_only": "N",
            "categories": [{"category_name": "ケーブル"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-005",
            "custom_code": "DEMO-005",
            "product_name": "【デモ】エレコム HDMI ディスプレイアダプタ",
            "sell_price": 1480,
            "consumer_price": 1580,
            "tax_rate": 0.1,
            "quantity": 8,
            "is_member_only": "N",
            "categories": [{"category_name": "アダプタ"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-006",
            "custom_code": "DEMO-006",
            "product_name": "【デモ】エレコム USBメモリ 64GB",
            "sell_price": 2480,
            "consumer_price": 2480,
            "tax_rate": 0.1,
            "quantity": 0,
            "is_member_only": "N",
            "categories": [{"category_name": "メモリ"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-007",
            "custom_code": "DEMO-007",
            "product_name": "【デモ】エレコム モニタースタンド",
            "sell_price": 4980,
            "consumer_price": 5480,
            "tax_rate": 0.1,
            "quantity": 3,
            "is_member_only": "N",
            "categories": [{"category_name": "スタンド"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-008",
            "custom_code": "DEMO-008",
            "product_name": "【デモ】エレコム LANケーブル Cat6A 5m",
            "sell_price": 1280,
            "consumer_price": 1380,
            "tax_rate": 0.1,
            "quantity": 12,
            "is_member_only": "N",
            "categories": [{"category_name": "ケーブル"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-009",
            "custom_code": "DEMO-009",
            "product_name": "【デモ】エレコム 電源タップ 6口",
            "sell_price": 1680,
            "consumer_price": 1780,
            "tax_rate": 0.1,
            "quantity": 7,
            "is_member_only": "N",
            "categories": [{"category_name": "電源"}],
            "variations": [],
        },
        {
            "system_code": "DEMO-010",
            "custom_code": "DEMO-010",
            "product_name": "【デモ】エレコム デュアルモニターアーム",
            "sell_price": 3480,
            "consumer_price": 3980,
            "tax_rate": 0.1,
            "quantity": 2,
            "is_member_only": "N",
            "categories": [{"category_name": "スタンド"}],
            "variations": [],
        },
    ]
