"""serve コマンド: 生成済みモックサイトをローカルプレビューする。"""
import http.server
import os
import sys
import threading
import webbrowser
from pathlib import Path

import click

from src.utils.logger import get_logger

logger = get_logger("ec_mockup.serve")


@click.command("serve")
@click.option("--port", default=8080, show_default=True, help="ポート番号")
@click.option("--host", default="127.0.0.1", show_default=True, help="バインドホスト")
@click.option("--no-browser", is_flag=True, default=False, help="ブラウザを自動で開かない")
@click.pass_context
def serve_cmd(ctx: click.Context, port: int, host: str, no_browser: bool) -> None:
    """生成済みモックサイトをローカルサーバで配信する。"""
    cfg = ctx.obj["config"]
    site_dir = cfg.app_output_dir

    if not site_dir.exists():
        click.echo(f"出力ディレクトリが存在しません: {site_dir}", err=True)
        click.echo("先に `ec-mockup build` を実行してください。", err=True)
        sys.exit(1)

    os.chdir(site_dir)

    url = f"http://{host}:{port}"
    logger.info("サーバ起動: %s (ディレクトリ: %s)", url, site_dir)
    click.echo(f"プレビュー: {url}")
    click.echo("停止するには Ctrl+C を押してください")

    if not no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    handler = http.server.SimpleHTTPRequestHandler
    with http.server.HTTPServer((host, port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("サーバを停止しました")
