"""作業ディレクトリ管理: work / output / tmp の生成・整理を担う。"""
from __future__ import annotations

import shutil
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger("ec_mockup.dirs")

_WORK_SUBDIRS = ["source", "data", "images", "live-site"]


def ensure_work_dirs(work_dir: Path) -> None:
    """work ディレクトリと標準サブディレクトリを作成する。"""
    for sub in _WORK_SUBDIRS:
        path = work_dir / sub
        path.mkdir(parents=True, exist_ok=True)
    logger.debug("work ディレクトリを確認しました: %s", work_dir)


def ensure_output_dir(output_dir: Path) -> None:
    """output ディレクトリを作成する。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("output ディレクトリを確認しました: %s", output_dir)


def ensure_temp_dir(temp_dir: Path) -> None:
    """temp ディレクトリを作成する。"""
    temp_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("temp ディレクトリを確認しました: %s", temp_dir)


def clean_temp_dir(temp_dir: Path) -> None:
    """temp ディレクトリの中身を削除する（ディレクトリ自体は残す）。"""
    if not temp_dir.exists():
        return
    for item in temp_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    logger.info("temp ディレクトリをクリアしました: %s", temp_dir)


def initialize_dirs(work_dir: Path, output_dir: Path, temp_dir: Path) -> None:
    """起動時に必要なディレクトリをすべて初期化する。"""
    ensure_work_dirs(work_dir)
    ensure_output_dir(output_dir)
    ensure_temp_dir(temp_dir)
