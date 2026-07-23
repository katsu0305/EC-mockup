"""設定ローダー: .env と config.yaml を読み込み、必須項目を検証する。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


# 必須キー一覧
#
# 現在はコマンドごとに必要な設定が異なるため、
# 起動時の一括必須チェックは行わない。
_REQUIRED_KEYS: list[str] = []


@dataclass
class AppConfig:
    # GitHub
    github_repository: str = ""
    github_ref: str = "main"
    github_subpaths: list[str] = field(default_factory=list)
    github_token: str = ""

    # ECDB API (legacy compatibility)
    ecdb_api_base_url: str = ""
    ecdb_api_key: str = ""
    ecdb_api_timeout_sec: int = 30
    ecdb_api_verify_ssl: bool = True

    # MakeShop images
    makeshop_public_base_url: str = ""
    makeshop_ftp_host: str = ""
    makeshop_ftp_port: int = 21
    makeshop_ftp_user: str = ""
    makeshop_ftp_password: str = ""
    makeshop_ftp_passive: bool = True
    makeshop_image_timeout_sec: int = 60
    makeshop_image_retry_count: int = 3

    # Live site
    live_site_base_url: str = ""
    live_site_login_url: str = ""
    live_site_username: str = ""
    live_site_password: str = ""
    live_site_headless: bool = True
    live_site_timeout_sec: int = 45

    # MSSQL (legacy compatibility)
    mssql_host: str = "192.168.244.101"
    mssql_port: int = 1433
    mssql_database: str = "ec_database"
    mssql_user: str = "sa"
    mssql_password: str = ""

    # App
    app_env: str = "development"
    app_log_level: str = "INFO"
    app_work_dir: Path = Path("./work")
    app_output_dir: Path = Path("./output/mock-site")
    app_temp_dir: Path = Path("./tmp")
    app_config_file: Path = Path("./config/mock-site.yaml")


def load_config(env_file: Path | None = None) -> AppConfig:
    """
    .env を読み込み AppConfig を返す。
    env_file 未指定時はプロジェクトルートの .env を自動検索する。
    """
    if env_file is None:
        env_file = _find_env_file()
    if env_file and env_file.exists():
        load_dotenv(env_file, override=False)

    _validate_required()

    cfg = AppConfig(
        github_repository=_get("GITHUB_REPOSITORY"),
        github_ref=_get("GITHUB_REF", "main"),
        github_subpaths=_get_list("GITHUB_SUBPATHS"),
        github_token=_get("GITHUB_TOKEN"),
        ecdb_api_base_url=_get("ECDB_API_BASE_URL"),
        ecdb_api_key=_get("ECDB_API_KEY"),
        ecdb_api_timeout_sec=_get_int("ECDB_API_TIMEOUT_SEC", 30),
        ecdb_api_verify_ssl=_get_bool("ECDB_API_VERIFY_SSL", True),
        makeshop_public_base_url=_get("MAKESHOP_PUBLIC_BASE_URL"),
        makeshop_ftp_host=_get("MAKESHOP_FTP_HOST"),
        makeshop_ftp_port=_get_int("MAKESHOP_FTP_PORT", 21),
        makeshop_ftp_user=_get("MAKESHOP_FTP_USER"),
        makeshop_ftp_password=_get("MAKESHOP_FTP_PASSWORD"),
        makeshop_ftp_passive=_get_bool("MAKESHOP_FTP_PASSIVE", True),
        makeshop_image_timeout_sec=_get_int("MAKESHOP_IMAGE_TIMEOUT_SEC", 60),
        makeshop_image_retry_count=_get_int("MAKESHOP_IMAGE_RETRY_COUNT", 3),
        live_site_base_url=_get("LIVE_SITE_BASE_URL"),
        live_site_login_url=_get("LIVE_SITE_LOGIN_URL"),
        live_site_username=_get("LIVE_SITE_USERNAME"),
        live_site_password=_get("LIVE_SITE_PASSWORD"),
        live_site_headless=_get_bool("LIVE_SITE_HEADLESS", True),
        live_site_timeout_sec=_get_int("LIVE_SITE_TIMEOUT_SEC", 45),
        mssql_host=_get("MSSQL_HOST", "192.168.244.101"),
        mssql_port=_get_int("MSSQL_PORT", 1433),
        mssql_database=_get("MSSQL_DATABASE", "ec_database"),
        mssql_user=_get("MSSQL_USER", "sa"),
        mssql_password=_get("MSSQL_PASSWORD", "Database@Leelee1!"),
        app_env=_get("APP_ENV", "development"),
        app_log_level=_get("APP_LOG_LEVEL", "INFO"),
        app_work_dir=Path(_get("APP_WORK_DIR", "./work")),
        app_output_dir=Path(_get("APP_OUTPUT_DIR", "./output/mock-site")),
        app_temp_dir=Path(_get("APP_TEMP_DIR", "./tmp")),
        app_config_file=Path(_get("APP_CONFIG_FILE", "./config/mock-site.yaml")),
    )

    # config.yaml で上書き（存在する場合のみ）
    if cfg.app_config_file.exists():
        _merge_yaml(cfg)

    return cfg


# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _find_env_file() -> Path | None:
    """カレントディレクトリから親へ向かって .env を探す。"""
    current = Path.cwd()
    for directory in [current, *current.parents]:
        candidate = directory / ".env"
        if candidate.exists():
            return candidate
    return None


def _validate_required() -> None:
    missing = [k for k in _REQUIRED_KEYS if not os.environ.get(k)]
    if missing:
        raise EnvironmentError(
            f"必須の環境変数が設定されていません: {', '.join(missing)}"
        )


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _get_int(key: str, default: int) -> int:
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def _get_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes")


def _get_list(key: str) -> list[str]:
    val = os.environ.get(key, "")
    return [v.strip() for v in val.split(",") if v.strip()] if val else []


def _merge_yaml(cfg: AppConfig) -> None:
    """config.yaml の値を AppConfig に反映する（.env 優先）。"""
    try:
        with cfg.app_config_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return

    # GitHub subpaths を yaml から補完
    if not cfg.github_subpaths:
        subpaths = (
            data.get("source", {}).get("github", {}).get("subpaths", [])
        )
        if isinstance(subpaths, list):
            cfg.github_subpaths = subpaths
