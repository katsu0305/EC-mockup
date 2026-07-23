"""静的サイトビルダー: テンプレート + データ → output/mock-site を生成する。"""
from __future__ import annotations

import shutil
from pathlib import Path

from src.builder.models import ProductDetail, SiteContext
from src.builder.normalizer import load_site_context
from src.builder.renderer import Renderer
from src.config.loader import AppConfig
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.static_builder")

_NOT_IMPL_HTML = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<title>未対応ページ</title></head>
<body style="font-family:sans-serif;padding:2rem">
<h1>このページはモックでは未対応です</h1>
<p><a href="../index.html">トップへ戻る</a></p>
</body></html>"""

_OFFLINE_FONT_CSS = """/* Offline fallback stylesheet for Noto Sans JP references. */
html,
body,
button,
input,
select,
textarea {
    font-family: "Noto Sans JP", "Hiragino Kaku Gothic ProN", "Yu Gothic", "Meiryo", sans-serif;
}
"""

_OFFLINE_FA_CSS = """/* Offline lightweight fallback for Font Awesome classes. */
.fa,
.fas,
.far,
.fal,
.fab,
[class^="fa-"],
[class*=" fa-"] {
    display: inline-block;
    font-style: normal;
    line-height: 1;
}

.fa::before,
.fas::before,
.far::before,
.fal::before,
.fab::before,
[class^="fa-"]::before,
[class*=" fa-"]::before {
    content: "";
}
"""

_OFFLINE_JQUERY_STUB = """/* Offline jQuery fallback: minimal no-op shim */
(function (global) {
    function StubCollection() {}
    var p = StubCollection.prototype;
    p.on = p.off = p.addClass = p.removeClass = p.toggleClass = p.slideToggle = p.hide = p.show = p.css = p.attr = p.removeAttr = p.text = p.html = p.append = p.prepend = p.trigger = function () { return this; };
    p.val = function () { return ""; };
    p.each = function () { return this; };
    p.get = function () { return null; };
    p.first = function () { return this; };
    p.ready = function (fn) { if (typeof fn === "function") { fn(); } return this; };

    function $(arg) {
        if (typeof arg === "function") {
            arg();
            return new StubCollection();
        }
        return new StubCollection();
    }

    $.fn = StubCollection.prototype;
    global.$ = global.jQuery = $;
})(window);
"""


def build(cfg: AppConfig) -> Path:
    """
    全ページを生成して output/mock-site へ出力する。
    戻り値は出力ディレクトリ。
    """
    source_dir = cfg.app_work_dir / "source"
    if not source_dir.exists():
        raise FileNotFoundError(f"work/source が存在しません。先に fetch-source を実行してください: {source_dir}")

    out = cfg.app_output_dir
    out.mkdir(parents=True, exist_ok=True)
    for child in out.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    ctx = load_site_context(cfg)
    logger.info("ビルド開始: 商品%d件 カテゴリ%d件", len(ctx.products), len(ctx.categories))

    # 1. assets コピー
    _copy_assets(source_dir, out, cfg)

    # 2. トップページ
    renderer = Renderer(source_dir, ctx, depth=0)
    _write(out / "index.html", renderer.render_top())
    logger.info("生成: index.html")

    # 3. 商品詳細ページ
    prod_dir = out / "products"
    prod_dir.mkdir(exist_ok=True)
    for product in ctx.products:
        r = Renderer(source_dir, ctx, depth=1)
        _write(prod_dir / f"{product.system_code}.html", r.render_detail(product))
    logger.info("生成: products/ (%d ページ)", len(ctx.products))

    # 4. カテゴリ一覧ページ
    cat_dir = out / "categories"
    cat_dir.mkdir(exist_ok=True)
    for cat in ctx.categories:
        r = Renderer(source_dir, ctx, depth=1)
        slug = cat.name.replace(" ", "_").replace("/", "_")
        _write(cat_dir / f"{slug}.html", r.render_category(cat))
    logger.info("生成: categories/ (%d ページ)", len(ctx.categories))

    # 5. お知らせページ
    news_dir = out / "news"
    news_dir.mkdir(exist_ok=True)
    r = Renderer(source_dir, ctx, depth=1)
    _write(news_dir / "index.html", r.render_news_list(ctx.news_items))
    logger.info("生成: news/index.html")

    # 6. 未対応ページ (カート、会員登録等)
    for stub in ("cart.html", "login.html", "mypage.html", "company.html",
                 "contract.html", "policy.html"):
        _write(out / stub, _NOT_IMPL_HTML)

    # 7. サマリ表示
    total = _count_files(out)
    logger.info("ビルド完了: %s (%d ファイル)", out, total)
    return out


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _copy_assets(source_dir: Path, out: Path, cfg: AppConfig) -> None:
    """CSS / JS / 画像 assets を output へコピーする。"""
    # all.css / all.js を css/ js/ フラットディレクトリへコピー（日本語パス回避）
    css_dir = out / "css"
    js_dir = out / "js"
    css_dir.mkdir(exist_ok=True)
    js_dir.mkdir(exist_ok=True)

    for f in source_dir.glob("original/**/*.css"):
        shutil.copy2(f, css_dir / f.name)
    for f in source_dir.glob("original/**/*.js"):
        shutil.copy2(f, js_dir / f.name)

    # assets/ ディレクトリ全体
    src_assets = source_dir / "assets"
    if src_assets.exists():
        dst_assets = out / "assets"
        if dst_assets.exists():
            shutil.rmtree(dst_assets)
        shutil.copytree(src_assets, dst_assets)

    # work/images/ ディレクトリ全体（ダウンロード済み商品画像）
    src_images = cfg.app_work_dir / "images"
    if src_images.exists():
        dst_images = out / "work" / "images"
        if dst_images.exists():
            shutil.rmtree(dst_images)
        shutil.copytree(src_images, dst_images)
        logger.debug("work/images コピー完了")

    _ensure_offline_assets(out)

    logger.debug("assets コピー完了")


def _ensure_offline_assets(out: Path) -> None:
    """file:// 表示で必要な最低限の代替アセットを保証する。"""
    # fonts / fontawesome fallback CSS
    fonts_css = out / "assets" / "vendor" / "fonts" / "noto-sans-jp.css"
    fa_css = out / "assets" / "vendor" / "fontawesome" / "all.min.css"
    fonts_css.parent.mkdir(parents=True, exist_ok=True)
    fa_css.parent.mkdir(parents=True, exist_ok=True)
    if not fonts_css.exists():
        fonts_css.write_text(_OFFLINE_FONT_CSS, encoding="utf-8")
    if not fa_css.exists():
        fa_css.write_text(_OFFLINE_FA_CSS, encoding="utf-8")

    # jquery fallback (CDN未参照化のためローカルファイルを常に用意)
    jquery_js = out / "assets" / "vendor" / "jquery" / "jquery-3.7.1.min.js"
    jquery_js.parent.mkdir(parents=True, exist_ok=True)
    if not jquery_js.exists():
        jquery_js.write_text(_OFFLINE_JQUERY_STUB, encoding="utf-8")

    # payment logo placeholders
    payment_dir = out / "assets" / "images" / "payment"
    payment_dir.mkdir(parents=True, exist_ok=True)
    logos = {
        "visa.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40" viewBox="0 0 120 40" role="img" aria-label="VISA logo placeholder"><rect width="120" height="40" rx="6" fill="#1a1f71"/><text x="60" y="26" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#ffffff" font-weight="700">VISA</text></svg>',
        "mastercard.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40" viewBox="0 0 120 40" role="img" aria-label="MasterCard logo placeholder"><rect width="120" height="40" rx="6" fill="#111111"/><circle cx="52" cy="20" r="10" fill="#eb001b"/><circle cx="68" cy="20" r="10" fill="#f79e1b" fill-opacity="0.9"/><text x="60" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="8" fill="#ffffff" font-weight="700">MASTERCARD</text></svg>',
        "jcb.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40" viewBox="0 0 120 40" role="img" aria-label="JCB logo placeholder"><rect width="120" height="40" rx="6" fill="#003a88"/><text x="60" y="26" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#ffffff" font-weight="700">JCB</text></svg>',
        "amex.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40" viewBox="0 0 120 40" role="img" aria-label="AMEX logo placeholder"><rect width="120" height="40" rx="6" fill="#2e77bb"/><text x="60" y="26" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#ffffff" font-weight="700">AMEX</text></svg>',
        "diners.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40" viewBox="0 0 120 40" role="img" aria-label="Diners logo placeholder"><rect width="120" height="40" rx="6" fill="#006272"/><text x="60" y="26" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#ffffff" font-weight="700">DINERS</text></svg>',
    }
    for name, content in logos.items():
        target = payment_dir / name
        if not target.exists():
            target.write_text(content, encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _count_files(directory: Path) -> int:
    return sum(1 for _ in directory.rglob("*") if _.is_file())
