import os

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request

import app
import security_controls


def make_request(origin: str | None = None) -> Request:
    headers = []
    if origin:
        headers.append((b"origin", origin.encode()))
    return Request({
        "type": "http",
        "method": "POST",
        "scheme": "https",
        "server": ("phfd-capital.web.app", 443),
        "path": "/admin/applications/demo/status",
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 1234),
    })


def test_same_origin_admin_write_allowed():
    security_controls.enforce_same_origin(make_request("https://phfd-capital.web.app"))


def test_cross_site_admin_write_blocked():
    with pytest.raises(HTTPException) as exc:
        security_controls.enforce_same_origin(make_request("https://evil.example"))
    assert exc.value.status_code == 403


def test_cloud_run_rejects_default_password(monkeypatch):
    monkeypatch.setenv("K_SERVICE", "phfd-capital")
    with pytest.raises(RuntimeError):
        security_controls.validate_production_config(security_controls.DEFAULT_ADMIN_PASSWORD)


def test_cloud_run_accepts_strong_password(monkeypatch):
    monkeypatch.setenv("K_SERVICE", "phfd-capital")
    security_controls.validate_production_config("correct-horse-battery-staple")


def test_public_pages_receive_security_headers():
    with TestClient(app.app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "object-src 'none'" in response.headers["content-security-policy"]


def test_admin_post_requires_same_origin():
    with TestClient(app.app) as client:
        response = client.post("/admin/applications/example/status")
    assert response.status_code == 403


def test_sensitive_pages_are_not_cached():
    with TestClient(app.app) as client:
        response = client.get("/apply")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store, max-age=0"
