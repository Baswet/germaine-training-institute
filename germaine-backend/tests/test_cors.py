"""CORS tests (Step 7 §22/§26) — opt-in only, public API only, never admin."""

import importlib
import os

import pytest


def _fresh_app(monkeypatch, origins=None):
    if origins is None:
        monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("CORS_ALLOWED_ORIGINS", origins)
    from app import create_app
    return create_app("testing")


def test_no_cors_headers_by_default(monkeypatch):
    app = _fresh_app(monkeypatch, origins=None)
    client = app.test_client()
    resp = client.get("/api/health", headers={"Origin": "https://example.com"})
    assert "Access-Control-Allow-Origin" not in resp.headers


def test_cors_headers_added_for_configured_origin(monkeypatch):
    app = _fresh_app(monkeypatch, origins="https://www.germaineinstitute.com")
    client = app.test_client()
    resp = client.get("/api/health", headers={"Origin": "https://www.germaineinstitute.com"})
    assert resp.headers.get("Access-Control-Allow-Origin") == "https://www.germaineinstitute.com"
    assert "Access-Control-Allow-Credentials" not in resp.headers


def test_cors_headers_not_added_for_unlisted_origin(monkeypatch):
    app = _fresh_app(monkeypatch, origins="https://www.germaineinstitute.com")
    client = app.test_client()
    resp = client.get("/api/health", headers={"Origin": "https://evil.example.com"})
    assert "Access-Control-Allow-Origin" not in resp.headers


def test_cors_never_applies_to_admin_routes(monkeypatch):
    app = _fresh_app(monkeypatch, origins="https://www.germaineinstitute.com")
    client = app.test_client()
    resp = client.get("/admin/login", headers={"Origin": "https://www.germaineinstitute.com"})
    assert "Access-Control-Allow-Origin" not in resp.headers
