"""export-data コマンド: MakeShop API から商品データを取得する。"""
import sys

import click

from src.utils.logger import get_logger

logger = get_logger("ec_mockup.export_data")


@click.command("export-data")
@click.option("--check", is_flag=True, default=False, help="接続確認のみ行う")
@click.pass_context
def export_data_cmd(ctx: click.Context, check: bool) -> None:
    """MakeShop API から公開中の商品データを取得する。"""
    from src.fetchers.data_exporter import check_connection, export_data

    cfg = ctx.obj["config"]
    if check:
        ok = check_connection(cfg)
        sys.exit(0 if ok else 1)
    try:
        dest = export_data(cfg)
        click.echo(f"保存先: {dest}")
    except Exception as e:
        logger.error("export-data 失敗: %s", e)
        sys.exit(1)
