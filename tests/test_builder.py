"""normalizer と renderer の単体テスト。"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.builder.models import ProductDetail, SiteContext
from src.builder.normalizer import _demo_items, _to_detail
from src.builder.renderer import Renderer, _replace_vars, _strip_conditional_blocks
from src.config.loader import AppConfig


# ---------------------------------------------------------------------------
# normalizer
# ---------------------------------------------------------------------------

class TestNormalizer:
    def _cfg(self) -> AppConfig:
        cfg = MagicMock(spec=AppConfig)
        cfg.app_work_dir = Path("./work")
        cfg.makeshop_public_base_url = "https://gigaplus.makeshop.jp/groxidirect1"
        return cfg

    def test_demo_items_not_empty(self) -> None:
        items = _demo_items()
        assert len(items) >= 1

    def test_to_detail_basic(self) -> None:
        cfg = self._cfg()
        item = {
            "system_code": "TEST-001",
            "custom_code": "TEST-001",
            "product_name": "テスト商品",
            "sell_price": 1980,
            "consumer_price": 1980,
            "tax_rate": 0.1,
            "quantity": 5,
            "is_member_only": "N",
            "categories": [{"category_name": "テストカテゴリ"}],
            "variations": [],
        }
        detail = _to_detail(item, cfg)
        assert detail.system_code == "TEST-001"
        assert detail.name == "テスト商品"
        assert detail.sell_price == 1980
        assert not detail.is_soldout
        assert "テストカテゴリ" in detail.categories

    def test_soldout_when_quantity_zero(self) -> None:
        cfg = self._cfg()
        item = {
            "system_code": "TEST-002",
            "custom_code": "TEST-002",
            "product_name": "在庫なし商品",
            "sell_price": 500,
            "consumer_price": 500,
            "tax_rate": 0.1,
            "quantity": 0,
            "is_member_only": "N",
            "categories": [],
            "variations": [],
        }
        detail = _to_detail(item, cfg)
        assert detail.is_soldout

    def test_sale_when_consumer_price_higher(self) -> None:
        cfg = self._cfg()
        item = {
            "system_code": "SALE-001",
            "custom_code": "SALE-001",
            "product_name": "セール商品",
            "sell_price": 800,
            "consumer_price": 1200,
            "tax_rate": 0.1,
            "quantity": 3,
            "is_member_only": "N",
            "categories": [],
            "variations": [],
        }
        detail = _to_detail(item, cfg)
        assert detail.is_sale


# ---------------------------------------------------------------------------
# renderer helpers
# ---------------------------------------------------------------------------

class TestRendererHelpers:
    def test_replace_vars_simple(self) -> None:
        result = _replace_vars("<title><{$page.title}></title>", {"page.title": "テスト"})
        assert result == "<title>テスト</title>"

    def test_replace_vars_missing_key(self) -> None:
        result = _replace_vars("<{$unknown.key}>", {})
        assert result == ""

    def test_replace_vars_with_filter(self) -> None:
        result = _replace_vars("<{$item.name|escape:html}>", {"item.name": "商品A"})
        assert result == "商品A"

    def test_strip_conditional_false_block(self) -> None:
        tmpl = "<{if $member.is_logged_in}>秘密の内容<{/if}>"
        result = _strip_conditional_blocks(tmpl, {})
        assert "秘密の内容" not in result

    def test_strip_section_loop(self) -> None:
        tmpl = "<{section name=i loop=$items}>ループ内<{/section}>"
        result = _strip_conditional_blocks(tmpl, {})
        assert "ループ内" not in result


# ---------------------------------------------------------------------------
# static builder smoke test
# ---------------------------------------------------------------------------

class TestStaticBuilderSmoke:
    def test_build_with_demo_data(self, tmp_path: Path) -> None:
        """デモデータで build が例外なく完了することを確認する。"""
        from src.builder.static_builder import build

        source_dir = tmp_path / "work" / "source"
        # 最小限のテンプレートディレクトリを用意
        for subdir, filename, content in [
            ("original/02_トップ", "top.html", "<html><body><{$module.header}><{$module.special}><{$module.footer}></body></html>"),
            ("original/02_トップ", "top.css", "body{}"),
            ("original/03_商品カテゴリー", "category.html", "<html><body><{$module.header}><{$module.footer}></body></html>"),
            ("original/03_商品カテゴリー", "category.css", "body{}"),
            ("original/05_商品詳細", "detail.html", "<html><body><{$module.header}><{$module.footer}></body></html>"),
            ("original/05_商品詳細", "detail.css", "body{}"),
            ("original/09_お知らせ一覧", "announce.html", "<html><body><{$module.header}><{$module.footer}></body></html>"),
            ("original/09_お知らせ一覧", "announce.css", "body{}"),
            ("original/18_モジュール管理", "01_header.html", "<header><{$shop.name}></header>"),
            ("original/18_モジュール管理", "03_footer.html", "<footer><{$shop.name}></footer>"),
        ]:
            d = source_dir / subdir
            d.mkdir(parents=True, exist_ok=True)
            (d / filename).write_text(content, encoding="utf-8")

        cfg = MagicMock(spec=AppConfig)
        cfg.app_work_dir = tmp_path / "work"
        cfg.app_output_dir = tmp_path / "output" / "mock-site"
        cfg.makeshop_public_base_url = "https://gigaplus.makeshop.jp/groxidirect1"

        out = build(cfg)
        assert (out / "index.html").exists()
        assert (out / "products").is_dir()
        assert (out / "categories").is_dir()
