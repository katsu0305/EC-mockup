"""Live Site Inspector: 実ショップへログインして HTML/CSS/JS を取得する。"""
from __future__ import annotations

import json
import time
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

import requests

from src.config.loader import AppConfig
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.live_site_inspector")

_DEFAULT_PAGES: dict[str, str] = {
    "top": "/",
    "category": "/shop/",
    "news": "/info/",
}


def login_check(cfg: AppConfig) -> bool:
    """ログインが成功するか確認する。成功した場合 True を返す。"""
    from playwright.sync_api import sync_playwright

    logger.info("login-check 開始: %s", cfg.live_site_login_url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=cfg.live_site_headless)
        try:
            ctx = browser.new_context()
            page = ctx.new_page()
            page.goto(
                cfg.live_site_login_url,
                wait_until="networkidle",
                timeout=cfg.live_site_timeout_sec * 1000,
            )
            page.locator("[name='login_id']").fill(cfg.live_site_username)
            page.locator("[name='password']").fill(cfg.live_site_password)
            page.locator("button[type='submit']").click()
            page.wait_for_load_state("networkidle", timeout=cfg.live_site_timeout_sec * 1000)

            success = page.locator(".header-menu").count() > 0
            logger.info("ログイン%s", "成功" if success else "失敗（成功セレクタ未検出）")
            return success
        finally:
            browser.close()


def capture_pages(
    cfg: AppConfig,
    pages: list[str],
    limit: int = 10,
    capture_screenshot: bool = False,
) -> Path:
    """指定ページ群をログイン後に取得して work/live-site へ保存する。"""
    from playwright.sync_api import sync_playwright

    dest = cfg.app_work_dir / "live-site"
    dest.mkdir(parents=True, exist_ok=True)

    base = cfg.live_site_base_url.rstrip("/")
    target_urls = _resolve_page_paths(pages, base)[:limit]
    logger.info("capture-live-site 開始: %d ページ", len(target_urls))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=cfg.live_site_headless)
        ctx = browser.new_context()
        _do_login(ctx, cfg)

        results: list[dict] = []
        for url in target_urls:
            info = _capture_one(ctx, url, dest, cfg, capture_screenshot)
            results.append(info)
            time.sleep(0.5)

        browser.close()

    (dest / "meta.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("capture-live-site 完了: %s", dest)
    return dest


# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _do_login(ctx, cfg: AppConfig) -> None:
    """ログインして認証済みセッションを context に保持する。"""
    page = ctx.new_page()
    try:
        page.goto(
            cfg.live_site_login_url,
            wait_until="networkidle",
            timeout=cfg.live_site_timeout_sec * 1000,
        )
        page.locator("[name='login_id']").fill(cfg.live_site_username)
        page.locator("[name='password']").fill(cfg.live_site_password)
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle", timeout=cfg.live_site_timeout_sec * 1000)
        logger.info("ログイン完了")
    finally:
        page.close()


def _capture_one(
    ctx,
    url: str,
    dest: Path,
    cfg: AppConfig,
    capture_screenshot: bool,
) -> dict:
    """1 ページを取得して保存し、メタ情報を返す。"""
    page = ctx.new_page()
    css_urls: list[str] = []
    js_urls: list[str] = []

    def on_response(response) -> None:
        ct = response.headers.get("content-type", "")
        if "text/css" in ct:
            css_urls.append(response.url)
        elif "javascript" in ct:
            js_urls.append(response.url)

    page.on("response", on_response)

    try:
        page.goto(url, wait_until="networkidle", timeout=cfg.live_site_timeout_sec * 1000)
        html = page.content()
    except Exception as e:
        logger.warning("取得失敗: %s (%s)", url, e)
        page.close()
        return {"url": url, "status": "error", "error": str(e)}

    slug = _url_to_slug(url)
    page_dir = dest / slug
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "index.html").write_text(html, encoding="utf-8")

    if capture_screenshot:
        page.screenshot(path=str(page_dir / "screenshot.png"), full_page=True)

    page.close()

    saved_css = _save_assets(css_urls, page_dir / "css")
    saved_js = _save_assets(js_urls, page_dir / "js")

    logger.info("保存: %s -> %s (css=%d js=%d)", url, slug, len(saved_css), len(saved_js))
    return {
        "url": url,
        "status": "ok",
        "slug": slug,
        "css_count": len(saved_css),
        "js_count": len(saved_js),
        "screenshot": capture_screenshot,
    }


def _save_assets(urls: list[str], dest_dir: Path) -> list[Path]:
    saved: list[Path] = []
    seen: set[str] = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            filename = PurePosixPath(urlparse(url).path).name or "asset"
            dest_dir.mkdir(parents=True, exist_ok=True)
            target = dest_dir / filename
            target.write_bytes(resp.content)
            saved.append(target)
        except Exception as e:
            logger.debug("アセット取得失敗: %s (%s)", url, e)
    return saved


def _url_to_slug(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path.strip("/").replace("/", "_") or "top"


def _resolve_page_paths(pages: list[str], base: str) -> list[str]:
    result: list[str] = []
    for p in pages:
        if p.startswith("http"):
            result.append(p)
        elif p in _DEFAULT_PAGES:
            result.append(base + _DEFAULT_PAGES[p])
        else:
            result.append(base + "/" + p.lstrip("/"))
    return result
