"""GitHub からテンプレートソースを取得して work/source へ展開する。"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import requests

from src.config.loader import AppConfig
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.source_fetcher")

_GITHUB_ZIP_URL = "https://api.github.com/repos/{repo}/zipball/{ref}"


def fetch_source(cfg: AppConfig) -> Path:
    """
    GitHub から対象 subpaths のみ取得して work/source へ展開する。
    戻り値は展開先ディレクトリ。
    """
    if not cfg.github_repository:
        raise EnvironmentError("GITHUB_REPOSITORY が設定されていません")
    if not cfg.github_ref:
        raise EnvironmentError("GITHUB_REF が設定されていません")

    dest = cfg.app_work_dir / "source"
    dest.mkdir(parents=True, exist_ok=True)

    url = _GITHUB_ZIP_URL.format(repo=cfg.github_repository, ref=cfg.github_ref)
    headers = {"Accept": "application/vnd.github+json"}
    if cfg.github_token:
        headers["Authorization"] = f"Bearer {cfg.github_token}"

    logger.info(
        "GitHub からソースを取得します: %s @ %s",
        cfg.github_repository,
        cfg.github_ref,
    )

    resp = requests.get(url, headers=headers, timeout=60, stream=True)
    if resp.status_code == 401:
        raise PermissionError("GitHub 認証失敗 (401): GITHUB_TOKEN を確認してください")
    if resp.status_code == 403:
        raise PermissionError("GitHub アクセス拒否 (403): トークンのスコープまたは org 権限を確認してください")
    if resp.status_code == 404:
        raise FileNotFoundError(
            f"GitHub リポジトリまたは ref が見つかりません (404): "
            f"{cfg.github_repository} @ {cfg.github_ref}"
        )
    resp.raise_for_status()

    raw = b"".join(resp.iter_content(chunk_size=65536))
    logger.info("ダウンロード完了: %.1f KB", len(raw) / 1024)

    _extract_subpaths(raw, dest, cfg.github_subpaths)

    logger.info("展開完了: %s", dest)
    return dest


def _extract_subpaths(
    zip_bytes: bytes,
    dest: Path,
    subpaths: list[str],
) -> None:
    """
    zip の先頭ディレクトリ（GitHub が付けるランダムプレフィックス）を除いて
    subpaths にマッチするエントリのみ展開する。
    subpaths が空の場合は全ファイルを展開する。
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        entries = zf.infolist()
        if not entries:
            return

        # GitHub zip は "repo-<hash>/" というプレフィックスを持つ
        prefix = entries[0].filename.split("/")[0] + "/"

        for entry in entries:
            if entry.is_dir():
                continue

            # プレフィックスを除いた相対パス
            rel = entry.filename[len(prefix):]
            if not rel:
                continue

            if subpaths and not any(
                rel == sp or rel.startswith(sp.rstrip("/") + "/")
                for sp in subpaths
            ):
                continue

            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(entry.filename))

    logger.debug("subpaths=%s の展開が完了しました", subpaths or ["(全件)"])
