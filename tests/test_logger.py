"""ロガーのテスト（secret マスク確認）。"""
from __future__ import annotations

import logging

from src.utils.logger import SecretMaskingFormatter, get_logger


class TestSecretMasking:
    def _format(self, message: str) -> str:
        formatter = SecretMaskingFormatter(fmt="%(message)s")
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg=message,
            args=(), exc_info=None,
        )
        return formatter.format(record)

    def test_masks_token(self) -> None:
        result = self._format("GITHUB_TOKEN=ghp_abc123xyz")
        assert "ghp_abc123xyz" not in result
        assert "***" in result

    def test_masks_password(self) -> None:
        result = self._format("password=MySecretPass")
        assert "MySecretPass" not in result
        assert "***" in result

    def test_masks_api_key(self) -> None:
        result = self._format("api_key=8d93260044e2a4838c7a")
        assert "8d93260044e2a4838c7a" not in result
        assert "***" in result

    def test_plain_message_unchanged(self) -> None:
        result = self._format("ビルド開始")
        assert result == "ビルド開始"

    def test_logger_returns_same_instance(self) -> None:
        a = get_logger("ec_mockup.test")
        b = get_logger("ec_mockup.test")
        assert a is b
