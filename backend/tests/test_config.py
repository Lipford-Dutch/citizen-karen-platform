import os
import secrets
import subprocess
import sys
from pathlib import Path

import pytest
from dotenv import dotenv_values
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from app import config as config_module
from app.config import AppEnvironment, Settings
from app.db import ComplaintStore

VALID_JWT_SECRET = "VgU3G1XyFzrGgS5CprjHm7nRkwOxY6eA0DdB8cTiWqk"
VALID_FCC_ENDPOINT = "https://connector.example.test/fcc/robocall"


def _valid_shared_settings(**overrides):
    values = {
        "app_env": AppEnvironment.PRODUCTION,
        "database_url": "postgresql+psycopg://app:password@db.example.test/app?sslmode=verify-full",
        "jwt_secret": VALID_JWT_SECRET,
        "demo_mode": False,
        "fcc_connector_mode": "network",
        "fcc_api_url": VALID_FCC_ENDPOINT,
        "fcc_approved_endpoints": VALID_FCC_ENDPOINT,
        "cors_origins": "https://app.example.test",
        "redis_url": "rediss://redis.example.test:6379/0",
        "otel_exporter_otlp_endpoint": "https://otel.example.test:4318",
    }
    values.update(overrides)
    return Settings(**values)


def test_local_defaults_remain_developer_friendly():
    config = Settings()
    assert config.app_env == AppEnvironment.LOCAL
    assert config.demo_mode is True
    assert config.fcc_connector_mode == "simulate"
    assert config.allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_default_sqlite_creates_missing_parent_when_launched_from_backend(
    tmp_path, monkeypatch
):
    backend_dir = tmp_path / "checkout" / "backend"
    backend_dir.mkdir(parents=True)
    database_path = backend_dir / "data" / "citizen-karen.db"
    assert not database_path.parent.exists()

    monkeypatch.chdir(backend_dir)
    monkeypatch.setattr(config_module, "DEFAULT_SQLITE_PATH", database_path)
    monkeypatch.setattr(config_module.settings, "app_env", AppEnvironment.TEST)
    monkeypatch.setattr(config_module.settings, "database_url", None)
    monkeypatch.setattr(config_module.settings, "citizen_karen_db_path", None)

    store = ComplaintStore()
    try:
        store.init()
        assert database_path.parent.is_dir()
        assert database_path.is_file()
        assert store.ready() is True
    finally:
        store.engine.dispose()


def test_env_example_sqlite_url_targets_backend_data_from_documented_cwd(
    monkeypatch,
):
    backend_dir = Path(__file__).resolve().parents[1]
    repository_root = backend_dir.parent
    example = dotenv_values(repository_root / ".env.example")
    database_url = example["DATABASE_URL"]
    assert database_url is not None

    monkeypatch.chdir(backend_dir)
    database_path = Path(make_url(database_url).database or "").resolve()
    assert database_path == backend_dir / "data" / "citizen-karen.db"


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({"jwt_secret": "replace-before-any-shared-deployment"}, "JWT_SECRET"),
        ({"jwt_secret": "A" * 64}, "diversity"),
        ({"jwt_secret": "demo_" + "Ab9-" * 12}, "predictable"),
        (
            {"jwt_secret": "ABCDEFGHIJKLMNOPABCDEFGHIJKLMNOPABCDEFGHIJKLMNOP"},
            "periodic",
        ),
        (
            {"jwt_secret": "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF"},
            "periodic",
        ),
        (
            {"jwt_secret": "AbCdEfGhIjKlMnOpAbCdEfGhIjKlMnOpAbCdEfGhIjKlMnOp"},
            "periodic",
        ),
        ({"demo_mode": True}, "DEMO_MODE"),
        ({"fcc_connector_mode": "simulate"}, "FCC_CONNECTOR_MODE"),
        ({"database_url": "sqlite:///data/app.db"}, "SQLite"),
        (
            {"database_url": "postgresql+psycopg://app:password@db.example.test/app"},
            "PostgreSQL",
        ),
        (
            {
                "database_url": "postgresql+psycopg://app:password@db.example.test/app?sslmode=require&sslmode=disable"
            },
            "PostgreSQL",
        ),
        ({"redis_url": "redis://redis.example.test:6379/0"}, "Redis"),
        ({"redis_url": "redis://redis:6379/0"}, "Redis"),
        (
            {"otel_exporter_otlp_endpoint": "http://otel.example.test:4318"},
            "OTLP",
        ),
        ({"insecure_internal_hosts": "*"}, "INSECURE_INTERNAL_HOSTS"),
        ({"insecure_internal_hosts": "*.internal"}, "INSECURE_INTERNAL_HOSTS"),
        ({"insecure_internal_hosts": "foo*bar"}, "INSECURE_INTERNAL_HOSTS"),
        (
            {
                "insecure_internal_hosts": "redis",
                "redis_url": "redis://arbitrary-service:6379/0",
            },
            "Redis",
        ),
        ({"cors_origins": "*"}, "CORS_ORIGINS"),
        ({"cors_origins": "https://*.example.test"}, "wildcards"),
        ({"cors_origins": "http://app.example.test"}, "CORS_ORIGINS"),
        ({"cors_origins": "https://user@app.example.test"}, "credentials"),
        ({"cors_origins": "https://app.example.test/path"}, "path"),
        ({"cors_origins": "https://app.example.test?x=1"}, "query"),
        ({"cors_origins": "https://app.example.test#fragment"}, "fragment"),
        ({"cors_origins": "https://APP.example.test"}, "canonical"),
        ({"fcc_approved_endpoints": ""}, "FCC_APPROVED_ENDPOINTS"),
        ({"fcc_api_url": "http://connector.example.test/fcc"}, "HTTPS"),
        (
            {
                "fcc_api_url": "https://other.example.test/fcc",
            },
            "exactly match",
        ),
        (
            {
                "fcc_api_url": "https://user:pass@connector.example.test/fcc",
                "fcc_approved_endpoints": "https://user:pass@connector.example.test/fcc",
            },
            "credentials",
        ),
        (
            {
                "fcc_api_url": "https://connector.example.test/fcc#fragment",
                "fcc_approved_endpoints": "https://connector.example.test/fcc#fragment",
            },
            "fragment",
        ),
        (
            {
                "fcc_api_url": "https://127.0.0.1/fcc",
                "fcc_approved_endpoints": "https://127.0.0.1/fcc",
            },
            "loopback",
        ),
        (
            {
                "fcc_api_url": "https://10.0.0.8/fcc",
                "fcc_approved_endpoints": "https://10.0.0.8/fcc",
            },
            "private",
        ),
        (
            {
                "fcc_api_url": "https://169.254.1.2/fcc",
                "fcc_approved_endpoints": "https://169.254.1.2/fcc",
            },
            "link-local",
        ),
        ({"fcc_api_url": "https://connector.example.test:8443/fcc"}, "exactly match"),
    ],
)
def test_shared_environments_reject_unsafe_configuration(overrides, expected):
    with pytest.raises(ValidationError, match=expected):
        _valid_shared_settings(**overrides)


def test_valid_production_configuration_is_accepted():
    config = _valid_shared_settings()
    assert config.app_env == AppEnvironment.PRODUCTION


def test_token_urlsafe_32_secret_is_accepted():
    config = _valid_shared_settings(jwt_secret=secrets.token_urlsafe(32))
    assert config.app_env == AppEnvironment.PRODUCTION


def test_explicit_internal_hosts_allow_cleartext_shared_services():
    internal_fcc = "http://mock-fcc:8001/fcc/robocall"
    config = _valid_shared_settings(
        database_url="postgresql+psycopg://app:password@postgres:5432/app",
        redis_url="redis://redis:6379/0",
        otel_exporter_otlp_endpoint="http://otel-collector:4318",
        fcc_api_url=internal_fcc,
        fcc_approved_endpoints=internal_fcc,
        insecure_internal_hosts="postgres,redis,otel-collector,mock-fcc",
    )
    assert config.cleartext_internal_hosts == {
        "postgres",
        "redis",
        "otel-collector",
        "mock-fcc",
    }


def test_non_default_fcc_port_requires_and_accepts_exact_allowlist_entry():
    endpoint = "https://connector.example.test:8443/fcc/robocall"
    config = _valid_shared_settings(
        fcc_api_url=endpoint,
        fcc_approved_endpoints=endpoint,
    )
    assert config.fcc_api_url == endpoint


def test_invalid_production_environment_exits_before_application_import():
    backend_dir = Path(__file__).resolve().parents[1]
    environment = {
        **os.environ,
        "APP_ENV": "production",
        "DEMO_MODE": "true",
        "JWT_SECRET": "replace-before-any-shared-deployment",
        "FCC_CONNECTOR_MODE": "simulate",
        "FCC_APPROVED_ENDPOINTS": "",
        "CORS_ORIGINS": "*",
    }
    result = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=backend_dir,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "unsafe shared-environment configuration" in result.stderr
