"""MakeShop から商品画像・運用画像を取得して work/images へ保存する。"""
from __future__ import annotations

import ftplib
import json
import time
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

import requests

from src.config.loader import AppConfig
from src.utils.logger import get_logger

logger = get_logger("ec_mockup.image_fetcher")

_SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
_MAX_TOTAL_BYTES = 300 * 1024 * 1024  # 300 MB


def fetch_images_from_urls(
    cfg: AppConfig,
    urls: list[str],
    limit: int = 500,
) -> Path:
    """
    公開 URL のリストから画像をダウンロードして work/images へ保存する。
    戻り値は保存先ディレクトリ。
    """
    dest = cfg.app_work_dir / "images"
    dest.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    total_bytes = 0
    downloaded = 0

    for url in urls:
        if downloaded >= limit:
            logger.info("上限 %d 件に達したためスキップ", limit)
            break

        # 重複排除
        normalized = url.split("?")[0]
        if normalized in seen:
            continue
        seen.add(normalized)

        # 拡張子フィルタ
        ext = PurePosixPath(urlparse(normalized).path).suffix.lower()
        if ext not in _SUPPORTED_EXTS:
            continue

        # 相対パスで保存
        rel_path = _url_to_rel_path(cfg.makeshop_public_base_url, normalized)
        target = dest / rel_path
        if target.exists():
            continue

        try:
            data = _download_with_retry(
                normalized,
                timeout=cfg.makeshop_image_timeout_sec,
                retries=cfg.makeshop_image_retry_count,
            )
        except Exception as e:
            logger.warning("ダウンロード失敗: %s (%s)", normalized, e)
            continue

        if total_bytes + len(data) > _MAX_TOTAL_BYTES:
            logger.warning("合計サイズ上限 300MB に達したため停止")
            break

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        total_bytes += len(data)
        downloaded += 1
        logger.debug("保存: %s", target)

    logger.info("画像取得完了: %d 件 (%.1f MB)", downloaded, total_bytes / 1024 / 1024)
    return dest


def fetch_images_via_ftp(cfg: AppConfig, limit: int = 500) -> Path:
    """
    FTP 経由で /img/{custom_code}/ ディレクトリから商品画像をダウンロードする。
    戻り値は保存先ディレクトリ。
    """
    dest = cfg.app_work_dir / "images"
    dest.mkdir(parents=True, exist_ok=True)

    # products.json から custom_code 一覧を取得
    products_json = cfg.app_work_dir / "data" / "products.json"
    if not products_json.exists():
        logger.error("products.json が見つかりません: %s", products_json)
        return dest
    
    data = json.loads(products_json.read_text(encoding="utf-8"))
    items = data.get("items", [])
    custom_codes = [item.get("custom_code", "") for item in items if item.get("custom_code")]
    
    logger.info("FTP 接続: %s", cfg.makeshop_ftp_host)

    total_bytes = 0
    downloaded = 0

    with ftplib.FTP() as ftp:
        ftp.connect(cfg.makeshop_ftp_host, cfg.makeshop_ftp_port)
        ftp.login(cfg.makeshop_ftp_user, cfg.makeshop_ftp_password)
        if cfg.makeshop_ftp_passive:
            ftp.set_pasv(True)

        logger.info("FTP ログイン成功")
        
        # 各 custom_code の /img/{custom_code}/ ディレクトリを走査
        for custom_code in custom_codes:
            if downloaded >= limit:
                break
            
            ftp_dir = f"/img/{custom_code}"
            files = _list_ftp_files(ftp, ftp_dir, max_depth=2)
            
            for remote_path in files:
                if downloaded >= limit:
                    break
                
                ext = PurePosixPath(remote_path).suffix.lower()
                if ext not in _SUPPORTED_EXTS:
                    continue

                # ローカルパスを構築：/img/HCS-WFS03BK/file.jpg → img/HCS-WFS03BK/file.jpg
                target = dest / remote_path.lstrip("/")
                if target.exists():
                    continue

                try:
                    buf = bytearray()
                    ftp.retrbinary(f"RETR {remote_path}", buf.extend)
                    data_bytes = bytes(buf)
                except Exception as e:
                    logger.warning("FTP 取得失敗: %s (%s)", remote_path, e)
                    continue

                if total_bytes + len(data_bytes) > _MAX_TOTAL_BYTES:
                    logger.warning("合計サイズ上限 300MB に達したため停止")
                    break

                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data_bytes)
                total_bytes += len(data_bytes)
                downloaded += 1
                logger.debug("保存: %s (%.1f KB)", target, len(data_bytes) / 1024)

    logger.info("FTP 取得完了: %d 件 (%.1f MB)", downloaded, total_bytes / 1024 / 1024)
    return dest


# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _download_with_retry(url: str, timeout: int, retries: int) -> bytes:
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=timeout, stream=False)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            last_exc = e
            if attempt < retries - 1:
                wait = 2 ** attempt
                logger.debug("リトライ %d/%d: %s (wait=%ds)", attempt + 1, retries, url, wait)
                time.sleep(wait)
    raise last_exc or RuntimeError("download failed")


def _url_to_rel_path(base_url: str, url: str) -> str:
    """公開ベース URL を除いた相対パスを返す。"""
    base = base_url.rstrip("/")
    if url.startswith(base):
        return url[len(base):].lstrip("/")
    # ベース外 URL は netloc+path をそのまま使う
    parsed = urlparse(url)
    return (parsed.netloc + parsed.path).lstrip("/")


def _list_ftp_files(ftp: ftplib.FTP, directory: str, max_depth: int = 5, _depth: int = 0, _visited: set[str] | None = None) -> list[str]:
    """FTP サーバのディレクトリを再帰的に走査してファイルパス一覧を返す。
    
    Args:
        ftp: FTP 接続
        directory: 走査対象ディレクトリ
        max_depth: 最大再帰深度（デフォルト 5）
        _depth: 現在の深度（内部用）
        _visited: 訪問済みディレクトリ（ループ検出用）
    """
    if _visited is None:
        _visited = set()
    
    # 深度チェック
    if _depth >= max_depth:
        logger.debug("最大深度 %d に達したためスキップ: %s", max_depth, directory)
        return []
    
    # ループ検出
    norm_dir = directory.rstrip("/")
    if norm_dir in _visited:
        logger.debug("既訪問ディレクトリをスキップ: %s", directory)
        return []
    _visited.add(norm_dir)
    
    result: list[str] = []
    try:
        entries: list[str] = []
        ftp.retrlines(f"LIST {directory}", entries.append)
    except ftplib.error_perm:
        logger.debug("権限エラー: %s", directory)
        return result

    for entry in entries:
        parts = entry.split()
        if len(parts) < 9:
            continue
        name = parts[-1]
        is_dir = entry.startswith("d")
        full = f"{directory.rstrip('/')}/{name}"
        if is_dir:
            result.extend(_list_ftp_files(ftp, full, max_depth=max_depth, _depth=_depth+1, _visited=_visited))
        else:
            result.append(full)

    return result
