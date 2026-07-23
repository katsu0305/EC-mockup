"""fetch-images コマンド: MakeShop から画像を取得する。"""
import json
import sys
from pathlib import Path

import click

from src.utils.logger import get_logger

logger = get_logger("ec_mockup.fetch_images")


@click.command("fetch-images")
@click.option("--ftp/--no-ftp", default=False, help="FTP 経由で取得する（デフォルトは公開 URL）")
@click.option("--limit", default=500, show_default=True, help="取得上限件数")
@click.pass_context
def fetch_images_cmd(ctx: click.Context, ftp: bool, limit: int) -> None:
    """MakeShop から商品画像・運用画像を取得する。"""
    from src.fetchers.image_fetcher import fetch_images_from_urls, fetch_images_via_ftp

    cfg = ctx.obj["config"]
    try:
        if ftp:
            dest = fetch_images_via_ftp(cfg, limit=limit)
        else:
            urls = _collect_image_urls(cfg.app_work_dir / "data" / "products.json",
                                       cfg.makeshop_public_base_url)
            dest = fetch_images_from_urls(cfg, urls, limit=limit)
        click.echo(f"保存先: {dest}")
    except Exception as e:
        logger.error("fetch-images 失敗: %s", e)
        sys.exit(1)


def _collect_image_urls(products_json: Path, base_url: str) -> list[str]:
    """products.json から画像 URL を収集する。"""
    if not products_json.exists():
        logger.warning("products.json が見つかりません: %s", products_json)
        return []
    data = json.loads(products_json.read_text(encoding="utf-8"))
    urls: list[str] = []
    base = base_url.rstrip("/")
    for item in data.get("items", []):
        code = item.get("system_code", "")
        if code:
            urls.append(f"{base}/item/{code}_01.jpg")
    return urls
