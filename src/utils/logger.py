"""ログ基盤: secret マスク付きロガーを提供する。"""
from __future__ import annotations

import logging
import re


# マスク対象となるキーワード（大文字小文字無視）
_SECRET_PATTERNS = re.compile(
    r"(token|password|secret|api[_\-]?key|pat\b)",
    re.IGNORECASE,
)

_SECRET_VALUE_RE = re.compile(
    r"((?:token|password|secret|api[_\-]?key|pat)\s*[=:]\s*)(\S+)",
    re.IGNORECASE,
)

_MASK = "***"


class SecretMaskingFormatter(logging.Formatter):
    """ログメッセージ内の secret 値を伏せ字にするフォーマッター。"""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return _SECRET_VALUE_RE.sub(lambda m: m.group(1) + _MASK, original)


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    指定した名前のロガーを返す。
    同名ロガーが既にハンドラを持っている場合は再設定しない。
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)
    formatter = SecretMaskingFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


def configure_root_logger(level: str = "INFO") -> None:
    """アプリ起動時に一度だけ呼ぶルートロガー設定。"""
    get_logger("ec_mockup", level)
