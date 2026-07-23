"""use case 層: GUI / CLI 両方から呼べる実行単位。

各関数は AppConfig を受け取り、進捗コールバック (on_progress) で状態を通知する。
on_progress(step: str, message: str) の形式で呼び出す。
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from src.config.loader import AppConfig
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.usecase")

ProgressCallback = Callable[[str, str], None]


def _noop(step: str, message: str) -> None:
    pass


# ---------------------------------------------------------------------------
# 個別 use case
# ---------------------------------------------------------------------------

def run_fetch_source(
    cfg: AppConfig,
    ref: str | None = None,
    on_progress: ProgressCallback = _noop,
) -> Path:
    """GitHub からソースを取得する。"""
    from src.fetchers.source_fetcher import fetch_source

    if ref:
        cfg.github_ref = ref
    on_progress("fetch-source", f"GitHub から取得中: {cfg.github_repository} @ {cfg.github_ref}")
    dest = fetch_source(cfg)
    on_progress("fetch-source", f"完了: {dest}")
    return dest


def run_export_data(
    cfg: AppConfig,
    latest_only: bool = True,
    on_progress: ProgressCallback = _noop,
) -> Path | None:
    """ECDB API から商品データを取得する。失敗時は None を返す。"""
    from src.fetchers.data_exporter import export_data

    on_progress("export-data", "ECDB API から商品データを取得中...")
    try:
        dest = export_data(cfg, latest_only=latest_only)
        on_progress("export-data", f"完了: {dest}")
        return dest
    except Exception as e:
        on_progress("export-data", f"スキップ（API 未接続）: {e}")
        logger.warning("export-data をスキップ: %s", e)
        return None


def run_fetch_images(
    cfg: AppConfig,
    use_ftp: bool = False,
    limit: int = 500,
    on_progress: ProgressCallback = _noop,
) -> Path:
    """画像を取得する。"""
    import json
    from src.fetchers.image_fetcher import fetch_images_from_urls, fetch_images_via_ftp

    on_progress("fetch-images", f"画像取得中 mode={'FTP' if use_ftp else '公開URL'} limit={limit}")
    if use_ftp:
        dest = fetch_images_via_ftp(cfg, limit=limit)
    else:
        products_file = cfg.app_work_dir / "data" / "products.json"
        if products_file.exists():
            items = json.loads(products_file.read_text(encoding="utf-8")).get("items", [])
            base = cfg.makeshop_public_base_url.rstrip("/")
            urls = [f"{base}/item/{item['system_code']}_01.jpg" for item in items if item.get("system_code")]
        else:
            urls = []
        dest = fetch_images_from_urls(cfg, urls, limit=limit)
    on_progress("fetch-images", f"完了: {dest}")
    return dest


def run_build(
    cfg: AppConfig,
    on_progress: ProgressCallback = _noop,
) -> Path:
    """静的サイトを生成する。"""
    from src.builder.static_builder import build

    on_progress("build", "モックサイト生成中...")
    out = build(cfg)
    on_progress("build", f"完了: {out}")
    return out


def run_all(
    cfg: AppConfig,
    skip_fetch: bool = False,
    on_progress: ProgressCallback = _noop,
) -> Path:
    """fetch-source → export-data → build を順に実行する。"""
    if not skip_fetch:
        run_fetch_source(cfg, on_progress=on_progress)
        run_export_data(cfg, on_progress=on_progress)
    return run_build(cfg, on_progress=on_progress)
