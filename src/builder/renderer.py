"""MakeShop テンプレート構文を静的 HTML へ変換するレンダラー。"""
from __future__ import annotations

import html
import re
from pathlib import Path

from src.builder.models import (
    CategorySummary,
    NewsItem,
    ProductCard,
    ProductDetail,
    SiteContext,
)
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.renderer")

# MakeShop 変数パターン: <{$var.sub.sub2}> または <{$var|filter:arg}>
_VAR_RE = re.compile(r"<\{\s*\$([A-Za-z0-9_.|:\[\]]+)\s*\}>")
# 未対応構文を除去するパターン
_MAKESHOP_TAG_RE = re.compile(r"<\{[^}]*\}>")
# 画像 URL 置換: gigaplus.makeshop.jp/groxidirect1/
_MAKESHOP_IMG_RE = re.compile(
    r'(src=["\'])https://gigaplus\.makeshop\.jp/groxidirect1/([^"\']*)["\']'
)


class Renderer:
    def __init__(self, source_dir: Path, ctx: SiteContext, depth: int = 0):
        self._source = source_dir
        self._ctx = ctx
        self._depth = depth  # ディレクトリ深さ（相対パス計算用）

    # ------------------------------------------------------------------
    # Public: ページ別レンダリング
    # ------------------------------------------------------------------

    def _head_extra(self) -> str:
        """全ページ共通 CSS (all.css) と JS (all.js) を返す。"""
        import time
        _v = str(int(time.time() // 3600))  # 1時間単位でキャッシュバスト
        return (
            f'<link href="{self._css_path("all.css")}?v={_v}" rel="stylesheet">\n'
            f'<script src="{self._root_path("js/all.js")}" defer></script>'
        )

    def render_top(self) -> str:
        tmpl = self._load_template("original/02_トップ/top.html")
        header = self._render_header()
        footer = self._render_footer()
        product_cards = self._render_product_card_list(
            self._ctx.products[:12]
        )
        vars_: dict[str, str] = {
            "page.title": f"{self._ctx.shop_name} | トップ",
            "page.description": f"{self._ctx.shop_name} - エレコム製品を特別価格でお届けします",
            "page.canonical_url": "index.html",
            "page.css": self._css_path("top.css"),
            "shop.name": self._ctx.shop_name,
            "shop.favicon_url": self._ctx.favicon_url,
            "shop.logo_url": self._ctx.logo_url,
            "module.header": header,
            "module.footer": footer,
            "module.special": f'<ul class="item-list">{product_cards}</ul>',
            "module.banner": "",
            "module.banner_custom": "",
            "module.side": self._render_sidenav(),
            "module.new": "",
            "module.recommend": "",
            "module.ranking": "",
            "shop.mainvisual": "",
            "shop.comment": "",
            "makeshop.head": self._head_extra(),
            "makeshop.body_top": "",
        }
        return self._process(tmpl, vars_)

    def render_category(self, cat: CategorySummary) -> str:
        tmpl = self._load_template("original/03_商品カテゴリー/category.html")
        items_html = self._render_product_card_list(cat.products)
        vars_: dict[str, str] = {
            "page.title": f"{cat.name} | {self._ctx.shop_name}",
            "page.description": f"{cat.name}の商品一覧",
            "page.canonical_url": cat.url,
            "page.css": self._css_path("category.css"),
            "shop.name": self._ctx.shop_name,
            "shop.favicon_url": self._ctx.favicon_url,
            "shop.logo_url": self._ctx.logo_url,
            "category.name": html.escape(cat.name),
            "category.image_url": "",
            "module.header": self._render_header(),
            "module.footer": self._render_footer(),
            "module.side": self._render_sidenav(),
            "url.top": self._root_path("index.html"),
            "makeshop.head": self._head_extra(),
            "makeshop.body_top": "",
        }
        result = self._process(tmpl, vars_)
        result = result + f'\n<section class="main-section container"><ul class="item-list">{items_html}</ul></section>'
        return result

    def render_detail(self, product: ProductDetail) -> str:
        tmpl = self._load_template("original/05_商品詳細/detail.html")
        css = self._css_path("detail.css")
        price_str = f"￥{product.sell_price:,}"
        sold_out_html = '<p class="soldout-text">SOLD OUT</p>' if product.is_soldout else ""
        add_cart_html = (
            "" if product.is_soldout
            else '<button class="btn-cart" disabled>※モック: カート機能無効</button>'
        )
        variations_html = self._render_variations(product.variations)
        
        # Categories を HTML 文字列として生成
        categories_html = ""
        if product.categories:
            cat_links = []
            for cat in product.categories:
                cat_links.append(
                    f'<a href="../category/{cat.category_uid}.html">{html.escape(cat.category_name)}</a>'
                )
            categories_html = " / ".join(cat_links)
        
        vars_: dict[str, object] = {
            "page.title": f"{html.escape(product.name)} | {self._ctx.shop_name}",
            "page.description": html.escape(product.name),
            "page.canonical_url": product.detail_url,
            "page.css": css,
            "shop.name": self._ctx.shop_name,
            "shop.favicon_url": self._ctx.favicon_url,
            "shop.logo_url": self._root_path(self._ctx.logo_url),
            "item.name": html.escape(product.name),
            "item.sell_price": f"{product.sell_price:,}",
            "item.consumer_price": f"{product.consumer_price:,}" if product.consumer_price else "",
            "item.quantity": str(product.quantity),
            "item.is_soldout": "1" if product.is_soldout else "0",
            "item.image_L": self._root_path(product.image_url) if product.image_url and not product.image_url.startswith("http") else product.image_url,
            "item.image_M": self._root_path(product.image_url) if product.image_url and not product.image_url.startswith("http") else product.image_url,
            "item.code": html.escape(product.system_code),
            "item.description": product.description or "",
            "item.add_content": product.add_content or "",
            "item.categories_html": categories_html,
            "module.header": self._render_header(),
            "module.footer": self._render_footer(),
            "module.side": self._render_sidenav(),
            "url.top": self._root_path("index.html"),
            "makeshop.head": self._head_extra(),
            "makeshop.body_top": "",
        }
        result = self._process(tmpl, vars_)
        # 商品情報ブロックを本文末に追記
        # 画像パスを補正
        img_src = self._root_path(product.image_url) if product.image_url and not product.image_url.startswith("http") else product.image_url
        extra = f"""
<div class="mock-product-info container" style="padding:1rem">
  <h1 class="item-name">{html.escape(product.name)}</h1>
  <p class="item-price">{price_str}（税込）</p>
  <img src="{img_src}" alt="{html.escape(product.name)}" style="max-width:300px">
  {sold_out_html}
  {variations_html}
  {add_cart_html}
</div>"""
        return result + extra

    def render_news_list(self, news_items: list[NewsItem]) -> str:
        tmpl = self._load_template("original/09_お知らせ一覧/announce.html")
        css = self._css_path("announce.css")
        items_html = "".join(
            f'<li><span class="news-date">{n.date}</span>'
            f'<a href="{n.url}">{html.escape(n.title)}</a></li>'
            for n in news_items
        )
        vars_: dict[str, str] = {
            "page.title": f"お知らせ | {self._ctx.shop_name}",
            "page.description": "お知らせ一覧",
            "page.canonical_url": "news/index.html",
            "page.css": css,
            "shop.name": self._ctx.shop_name,
            "shop.favicon_url": self._ctx.favicon_url,
            "module.header": self._render_header(),
            "module.footer": self._render_footer(),
            "module.side": self._render_sidenav(),
            "url.top": self._root_path("index.html"),
            "makeshop.head": self._head_extra(),
            "makeshop.body_top": "",
        }
        result = self._process(tmpl, vars_)
        return result + f'<ul class="news-list container">{items_html}</ul>'

    # ------------------------------------------------------------------
    # Module renderers
    # ------------------------------------------------------------------

    def _render_header(self) -> str:
        tmpl = self._load_template("original/18_モジュール管理/01_header.html")
        vars_: dict[str, str] = {
            "shop.name": self._ctx.shop_name,
            "shop.logo_url": self._root_path(self._ctx.logo_url),
            "url.top": self._root_path("index.html"),
            "url.login": "#",
            "url.logout": "#",
            "url.member_entry": "#",
            "url.favorite": "#",
            "url.mypage": "#",
            "url.cart": "#",
            "member.is_logged_in": "0",
            "member.group_name": "",
            "cart.has_item": "0",
            "cart.total_quantity": "0",
            "shop.is_member_entry_enabled": "0",
        }
        return self._process(tmpl, vars_)

    def _render_footer(self) -> str:
        guide_html = self._load_template("original/18_モジュール管理/13_purchase-info.html")
        # MakeShop 変数を解決（サポートページURL等）
        guide_html = guide_html.replace("<{$url.support}>", "#")
        guide_html = _MAKESHOP_TAG_RE.sub("", guide_html)
        tmpl = self._load_template("original/18_モジュール管理/03_footer.html")
        vars_: dict[str, str] = {
            "shop.name": self._ctx.shop_name,
            "shop.address": self._ctx.shop_address,
            "url.top": self._root_path("index.html"),
            "url.company": self._root_path("company.html"),
            "url.contract": self._root_path("contract.html"),
            "url.policy": self._root_path("policy.html"),
        }
        return guide_html + self._process(tmpl, vars_)

    def _render_sidenav(self) -> str:
        tmpl = self._load_template("original/18_モジュール管理/02_sidenavi.html")
        
        # SiteContext のカテゴリから動的にメニューを生成
        cat_links = "".join(
            f'<li class="side-category-item"><a href="{self._root_path(c.url)}">{html.escape(c.name)}</a></li>'
            for c in self._ctx.categories
        )
        
        vars_: dict[str, str] = {
            "url.login": "#",
            "url.logout": "#",
            "url.member_entry": "#",
            "search_form.keyword_id": "keyword",
            "search_form.category_id": "category",
            "search_form.price_low_id": "price_low",
            "search_form.price_high_id": "price_high",
            "search_form.search_url": "#",
            "search.keyword": "",
            "search.price_low": "",
            "search.price_high": "",
            "member.is_logged_in": "0",
            "shop.is_member_entry_enabled": "0",
        }
        result = self._process(tmpl, vars_)
        # カテゴリーで探す セクション内の側category-listを置換
        result = result.replace(
            '<ul class="side-category-list">\n            </ul>',
            f'<ul class="side-category-list">{cat_links}</ul>'
        )
        return result

    def _render_product_card_list(
        self, products: list[ProductCard | ProductDetail]
    ) -> str:
        items_html = ""
        for p in products:
            sold_badge = '<p class="item-soldout">SOLD OUT</p>' if p.is_soldout else ""
            sale_badge = '<p class="item-sale">SALE</p>' if p.is_sale else ""
            url = self._root_path(p.detail_url)
            # 相対パスの場合は _root_path() で補正
            img_src = self._root_path(p.image_url) if p.image_url and not p.image_url.startswith("http") else p.image_url
            items_html += f"""
<li>
  <div class="item-icon">{sold_badge}{sale_badge}</div>
  <div class="item-list-image">
    <a href="{url}"><img src="{img_src}" alt="{html.escape(p.name)}" loading="lazy"></a>
  </div>
  <p class="item-name"><a href="{url}">{html.escape(p.name)}</a></p>
  <p class="price">￥{p.sell_price:,}<span>（税込）</span></p>
</li>"""
        return items_html

    def _render_variations(self, variations) -> str:
        if not variations:
            return ""
        opts = "".join(
            f'<option value="{v.variation_id}" {"disabled" if v.is_soldout else ""}>'
            f'{html.escape(v.name1)} {html.escape(v.name2)}'
            f'{"（在庫なし）" if v.is_soldout else ""}</option>'
            for v in variations
        )
        return f'<select class="variation-select">{opts}</select>'

    # ------------------------------------------------------------------
    # Template processing
    # ------------------------------------------------------------------

    def _process(self, tmpl: str, vars_: dict[str, str]) -> str:
        """
        MakeShop テンプレートを処理する。
        1. 条件ブロックを評価
        2. 変数を置換
        3. 未対応タグを除去
        4. 画像 URL をローカルパスへ置換
        """
        result = _strip_conditional_blocks(tmpl, vars_)
        result = _replace_vars(result, vars_)
        result = _MAKESHOP_TAG_RE.sub("", result)
        result = _rewrite_makeshop_images(result, self._root_path("work/images"))
        return result

    def _load_template(self, rel: str) -> str:
        path = self._source / rel
        if not path.exists():
            logger.warning("テンプレートが見つかりません: %s", path)
            return f"<!-- template not found: {rel} -->"
        return path.read_text(encoding="utf-8")

    def _css_path(self, filename: str) -> str:
        """フラット化された css/ ディレクトリへのパスを返す。"""
        return self._root_path(f"css/{filename}")

    def _root_path(self, rel: str) -> str:
        """出力ルートからの相対パスを depth に応じて補正する。"""
        prefix = "../" * self._depth
        return prefix + rel


# ---------------------------------------------------------------------------
# Template processing helpers
# ---------------------------------------------------------------------------

def _replace_vars(tmpl: str, vars_: dict[str, str]) -> str:
    """登録済み変数を置換する。"""
    def replacer(m: re.Match) -> str:
        key = m.group(1)
        # |escape:html や |number_format などフィルタを除去
        base_key = key.split("|")[0].strip()
        # 配列アクセス [i] を除去
        base_key = re.sub(r"\[[^\]]*\]", "", base_key)
        return vars_.get(base_key, "")
    return _VAR_RE.sub(replacer, tmpl)


def _strip_conditional_blocks(tmpl: str, vars_: dict[str, str]) -> str:
    """
    <{if ...}> ブロックを評価して不要なブランチを除去する。
    item.is_soldout の条件のみ処理し、その他の条件は維持する。
    """
    result = tmpl
    
    # item.is_soldout の値に基づいて条件処理（if/elseのみ）
    if vars_.get("item.is_soldout") == "1":
        # 売り切れの場合：<{if $item.is_soldout}>ブロックを保持、elseブロックを削除
        result = re.sub(
            r"<\{\s*if\s+\$item\.is_soldout\s*\}>(.*?)<\{\s*else\s*\}>.*?<\{/if\}>",
            r"\1",
            result,
            flags=re.DOTALL,
        )
    else:
        # 在庫ありの場合：<{if $item.is_soldout}>ブロックを削除、elseブロックを保持
        result = re.sub(
            r"<\{\s*if\s+\$item\.is_soldout\s*\}>.*?<\{\s*else\s*\}>(.*?)<\{/if\}>",
            r"\1",
            result,
            flags=re.DOTALL,
        )
    
    # 明示的に false の条件のみ削除
    false_conditions = {
        "member.is_logged_in", "cart.has_item", "shop.is_member_entry_enabled",
        "item.review.has_item", "category.image_url",
        "item.add_image.has_item", "item.icon.has_item",
    }
    
    for cond in false_conditions:
        # <{if $cond }> ブロックのみ削除、else/elseif は保持
        result = re.sub(
            r"<\{\s*if\s+\$" + re.escape(cond) + r"\s*\}>.*?<\{\s*else\s*\}>(.*?)<\{/if\}>",
            r"\1",
            result,
            flags=re.DOTALL,
        )
        # else なしの <{if $cond }> ブロックは削除
        result = re.sub(
            r"<\{\s*if\s+\$" + re.escape(cond) + r"\s*\}>.*?<\{/if\}>",
            "",
            result,
            flags=re.DOTALL,
        )
    
    # section ループを除去
    result = re.sub(r"<\{section[^}]*\}>.*?<\{/section\}>", "", result, flags=re.DOTALL)
    
    # 残りの if / else / elseif タグ除去
    result = re.sub(r"<\{else\}>.*?(?=<\{/if\}>)", "", result, flags=re.DOTALL)
    result = re.sub(r"<\{/if\}>", "", result)
    result = re.sub(r"<\{if[^}]*\}>", "", result)
    
    return result


def _rewrite_makeshop_images(html_str: str, local_images_root: str) -> str:
    """gigaplus.makeshop.jp の画像 URL をローカルパスへ置換する。
    ただし、実際にローカルファイルが存在する場合のみ置換。
    存在しない場合は公開 URL をそのまま使用。
    """
    from pathlib import Path
    
    def replacer(m):
        prefix = m.group(1)
        path = m.group(2)  # e.g., "item/000000000134_01.jpg"
        local_file = Path(local_images_root) / path
        
        if local_file.exists():
            # ローカルファイルが存在 → ローカルパスを使う
            return f"{prefix}{local_images_root}/{path}\""
        else:
            # ローカルファイルが存在しない → 公開 URL をそのまま使う
            # マッチした全文を返す（置換しない）
            return m.group(0)
    
    return _MAKESHOP_IMG_RE.sub(replacer, html_str)

