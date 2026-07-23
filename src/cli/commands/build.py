"""build コマンド: fetch-source → export-data → 静的サイト生成を実行する。"""
import sys

import click

from src.utils.logger import get_logger

logger = get_logger("ec_mockup.build")


@click.command("build")
@click.option("--skip-fetch", is_flag=True, default=False, help="入力取得をスキップしてビルドのみ実行する")
@click.pass_context
def build_cmd(ctx: click.Context, skip_fetch: bool) -> None:
    """モックサイトをビルドする（fetch-source → export-data → 生成）。"""
    from src.fetchers.data_exporter import export_data
    from src.fetchers.source_fetcher import fetch_source
    from src.builder.static_builder import build

    cfg = ctx.obj["config"]
    logger.info("build 開始 skip_fetch=%s", skip_fetch)

    if not skip_fetch:
        try:
            fetch_source(cfg)
        except Exception as e:
            logger.error("fetch-source 失敗: %s", e)
            sys.exit(1)
        try:
            export_data(cfg)
        except Exception as e:
            logger.warning("export-data 失敗（スキップして続行）: %s", e)

    try:
        out = build(cfg)
        click.echo(f"出力先: {out}")
    except Exception as e:
        logger.error("ビルド失敗: %s", e)
        sys.exit(1)
