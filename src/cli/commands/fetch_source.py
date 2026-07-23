"""fetch-source コマンド: GitHub からテンプレートを取得する。"""
import sys

import click

from src.utils.logger import get_logger

logger = get_logger("ec_mockup.fetch_source")


@click.command("fetch-source")
@click.option("--ref", default=None, help="取得する branch / tag / commit（未指定時は .env の GITHUB_REF を使用）")
@click.pass_context
def fetch_source_cmd(ctx: click.Context, ref: str | None) -> None:
    """GitHub からテンプレートソースを取得する。"""
    from src.fetchers.source_fetcher import fetch_source

    cfg = ctx.obj["config"]
    if ref:
        cfg.github_ref = ref
    try:
        dest = fetch_source(cfg)
        click.echo(f"展開先: {dest}")
    except Exception as e:
        logger.error("fetch-source 失敗: %s", e)
        sys.exit(1)
