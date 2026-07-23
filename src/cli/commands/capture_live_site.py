"""capture-live-site コマンド: 実ショップから HTML/CSS/JS を取得する雛形。"""
import click

from src.utils.logger import get_logger

logger = get_logger("ec_mockup.capture_live_site")

_PAGE_CHOICES = click.Choice(["top", "category", "product", "news"], case_sensitive=False)


@click.group("capture-live-site")
def capture_live_site_cmd() -> None:
    """実ショップから比較用スナップショットを取得する。"""


@capture_live_site_cmd.command("run")
@click.option("--pages", default="top", show_default=True, help="取得対象ページ種別（カンマ区切り）: top,category,product,news")
@click.option("--headless/--no-headless", default=True, help="ブラウザを headless で起動する")
@click.option("--capture-screenshot", is_flag=True, default=False, help="スクリーンショットも保存する")
@click.option("--limit", default=10, show_default=True, help="取得ページ数上限")
@click.pass_context
def run_cmd(ctx: click.Context, pages: str, headless: bool, capture_screenshot: bool, limit: int) -> None:
    """ログイン後のページを取得して work/live-site へ保存する。"""
    import sys
    from src.fetchers.live_site_inspector import capture_pages

    cfg = ctx.obj["config"]
    cfg.live_site_headless = headless
    try:
        dest = capture_pages(
            cfg,
            pages=pages.split(","),
            limit=limit,
            capture_screenshot=capture_screenshot,
        )
        click.echo(f"保存先: {dest}")
    except Exception as e:
        logger.error("capture-live-site 失敗: %s", e)
        sys.exit(1)


@capture_live_site_cmd.command("login-check")
@click.pass_context
def login_check_cmd(ctx: click.Context) -> None:
    """ログインが成功するか確認する。"""
    import sys
    from src.fetchers.live_site_inspector import login_check

    cfg = ctx.obj["config"]
    ok = login_check(cfg)
    if ok:
        click.echo("ログイン成功")
    else:
        click.echo("ログイン失敗", err=True)
        sys.exit(1)


@capture_live_site_cmd.command("diff")
def diff_cmd() -> None:
    """モックと実ショップの差分を確認する。"""
    logger.info("diff 開始")
    logger.info("[TODO] 差分確認実装")


@capture_live_site_cmd.command("clean")
def clean_cmd() -> None:
    """work/live-site を削除する。"""
    logger.info("clean 開始")
    logger.info("[TODO] クリーン実装")
