"""内部データモデル定義。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Category:
    """カテゴリ情報。"""
    category_uid: str
    category_name: str


@dataclass
class ProductCard:
    """カテゴリ一覧・検索結果等で使うカード表示用モデル。"""
    system_code: str
    name: str
    sell_price: int
    consumer_price: int
    image_url: str          # ローカル or 公開URL
    detail_url: str         # output/ 内の相対パス
    is_soldout: bool = False
    is_sale: bool = False
    category_name: str = ""
    category_url: str = ""


@dataclass
class Variation:
    variation_id: int
    name1: str = ""
    name2: str = ""
    quantity: int = 0
    is_soldout: bool = False


@dataclass
class ProductDetail:
    """商品詳細ページ用モデル。"""
    system_code: str
    custom_code: str
    name: str
    sell_price: int
    consumer_price: int
    tax_rate: float
    quantity: int
    image_url: str
    detail_url: str
    is_soldout: bool = False
    is_sale: bool = False
    is_member_only: bool = False
    variations: list[Variation] = field(default_factory=list)
    categories: list[Category] = field(default_factory=list)
    description: str = ""
    add_content: str = ""


@dataclass
class CategorySummary:
    """カテゴリページ用モデル。"""
    name: str
    url: str
    products: list[ProductCard] = field(default_factory=list)


@dataclass
class NewsItem:
    """お知らせ用モデル。"""
    title: str
    date: str
    url: str
    body: str = ""


@dataclass
class SiteContext:
    """サイト全体に渡すコンテキスト。"""
    shop_name: str = "ELECOM 4 YOU"
    shop_address: str = ""
    top_url: str = "index.html"
    logo_url: str = "assets/images/brand/logo/logo.png"
    favicon_url: str = ""
    products: list[ProductDetail] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)
    news_items: list[NewsItem] = field(default_factory=list)
