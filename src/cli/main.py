"""ec-mockup CLI エントリポイント。"""
from __future__ import annotations

import sys

import click

from src.cli.commands.build import build_cmd
from src.cli.commands.capture_live_site import capture_live_site_cmd
from src.cli.commands.export_data import export_data_cmd
from src.cli.commands.fetch_images import fetch_images_cmd
from src.cli.commands.fetch_source import fetch_source_cmd
from src.cli.commands.serve import serve_cmd
from src.config.loader import load_config
from src.utils.dirs import initialize_dirs
from src.utils.logger import configure_root_logger, get_logger

logger = get_logger("ec_mockup.cli")


@click.group()
@click.option(
    "--log-level",
    default=None,
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help="ログレベルを上書きする（未指定時は .env の APP_LOG_LEVEL を使用）",
)
@click.pass_context
def cli(ctx: click.Context, log_level: str | None) -> None:
    """ローカルモック生成ツール。"""
    ctx.ensure_object(dict)

    try:
        cfg = load_config()
    except EnvironmentError as e:
        click.echo(f"[ERROR] 設定エラー: {e}", err=True)
        sys.exit(1)

    level = log_level or cfg.app_log_level
    configure_root_logger(level)

    initialize_dirs(cfg.app_work_dir, cfg.app_output_dir, cfg.app_temp_dir)

    ctx.obj["config"] = cfg


cli.add_command(build_cmd)
cli.add_command(fetch_source_cmd)
cli.add_command(export_data_cmd)
cli.add_command(fetch_images_cmd)
cli.add_command(capture_live_site_cmd)
cli.add_command(serve_cmd)


if __name__ == "__main__":
    cli()
