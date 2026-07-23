"""設定ローダーのテスト。"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config.loader import AppConfig, load_config


class TestLoadConfig:
    def test_load_from_env(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "GITHUB_REPOSITORY=test-org/test-repo\n"
            "GITHUB_REF=main\n"
            "ECDB_API_BASE_URL=http://localhost:8000/api/v1\n"
            "ECDB_API_KEY=testkey\n",
            encoding="utf-8",
        )
        cfg = load_config(env_file)
        assert cfg.github_repository == "test-org/test-repo"
        assert cfg.github_ref == "main"
        assert cfg.ecdb_api_base_url == "http://localhost:8000/api/v1"
        assert cfg.ecdb_api_key == "testkey"

    def test_missing_required_raises(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("APP_ENV=development\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EnvironmentError, match="必須の環境変数"):
                load_config(env_file)

    def test_defaults(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "GITHUB_REPOSITORY=org/repo\n"
            "GITHUB_REF=main\n"
            "ECDB_API_BASE_URL=http://localhost:8000/api/v1\n"
            "ECDB_API_KEY=key\n",
            encoding="utf-8",
        )
        cfg = load_config(env_file)
        assert cfg.ecdb_api_timeout_sec == 30
        assert cfg.ecdb_api_verify_ssl is True
        assert cfg.makeshop_ftp_port == 21
        assert cfg.app_env == "development"
        assert cfg.app_log_level == "INFO"
