"""Verifies config loading is environment-variable-driven and secret-free."""

import os

from app.config import get_config, DevelopmentConfig, TestingConfig, ProductionConfig


def test_get_config_defaults_to_development(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    assert get_config() is DevelopmentConfig


def test_get_config_resolves_testing():
    assert get_config("testing") is TestingConfig


def test_get_config_resolves_production():
    assert get_config("production") is ProductionConfig


def test_no_hardcoded_database_credentials_in_base_config():
    # BaseConfig must read from the environment, never hardcode a real
    # connection string. Empty string is the expected "not set" default.
    from app.config import BaseConfig

    assert BaseConfig.SQLALCHEMY_DATABASE_URI == os.environ.get("DATABASE_URL", "")


def test_testing_config_uses_in_memory_sqlite_not_postgres():
    assert "sqlite" in TestingConfig.SQLALCHEMY_DATABASE_URI
    assert "postgres" not in TestingConfig.SQLALCHEMY_DATABASE_URI
