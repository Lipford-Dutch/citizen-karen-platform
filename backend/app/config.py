import base64
import binascii
import ipaddress
import math
import re
from collections import Counter
from enum import StrEnum
from pathlib import Path
from urllib.parse import SplitResult, urlsplit, urlunsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

DEFAULT_SQLITE_PATH = Path(__file__).resolve().parents[1] / "data" / "citizen-karen.db"
TOKEN_URLSAFE_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
COMMON_SECRET_MARKERS = {
    "change",
    "changeme",
    "demo",
    "example",
    "local",
    "password",
    "replace",
    "secret",
}


class AppEnvironment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Validated application configuration loaded exclusively from the environment."""

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )

    app_env: AppEnvironment = AppEnvironment.LOCAL
    database_url: str | None = None
    citizen_karen_db_path: str | None = None
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    demo_mode: bool = True
    async_submissions: bool = False
    jwt_secret: str = "local-demo-only-change-before-deployment"
    redis_url: str = "redis://localhost:6379/0"
    insecure_internal_hosts: str = ""
    submission_rate_limit_per_minute: int = Field(default=5, ge=1)
    fcc_connector_mode: str = "simulate"
    fcc_api_url: str = "http://localhost:8001/fcc/robocall"
    fcc_approved_endpoints: str = ""
    smtp_host: str = "mailhog"
    smtp_port: int = Field(default=1025, ge=1, le=65535)
    otel_exporter_otlp_endpoint: str | None = None
    otel_service_name: str = "citizen-karen-api"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.citizen_karen_db_path:
            return f"sqlite:///{Path(self.citizen_karen_db_path).resolve().as_posix()}"
        return f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def approved_fcc_endpoints(self) -> list[str]:
        return [
            endpoint.strip()
            for endpoint in self.fcc_approved_endpoints.split(",")
            if endpoint.strip()
        ]

    @property
    def cleartext_internal_hosts(self) -> set[str]:
        return {
            host.strip().lower()
            for host in self.insecure_internal_hosts.split(",")
            if host.strip()
        }

    def _validate_internal_host_allowlist(self) -> list[str]:
        errors: list[str] = []
        for host in self.cleartext_internal_hosts:
            if (
                "*" in host
                or "://" in host
                or "/" in host
                or "@" in host
                or any(character.isspace() for character in host)
            ):
                errors.append(
                    "INSECURE_INTERNAL_HOSTS must contain exact host names without URLs, ports, or wildcards"
                )
                continue
            try:
                parsed = urlsplit(f"//{host}")
                port = parsed.port
            except ValueError:
                errors.append(
                    "INSECURE_INTERNAL_HOSTS must contain exact host names without URLs, ports, or wildcards"
                )
                continue
            if parsed.hostname != host or port is not None:
                errors.append(
                    "INSECURE_INTERNAL_HOSTS must contain exact host names without URLs, ports, or wildcards"
                )
        return errors

    def _cleartext_allowed(self, hostname: str | None) -> bool:
        return bool(hostname and hostname.lower() in self.cleartext_internal_hosts)

    @staticmethod
    def _jwt_secret_error(secret: str) -> str | None:
        """Require a high-entropy token compatible with secrets.token_urlsafe(32)."""
        normalized = secret.strip()
        lowered = normalized.lower()
        if any(marker in lowered for marker in COMMON_SECRET_MARKERS):
            return "JWT_SECRET contains a common or predictable marker"
        if not TOKEN_URLSAFE_PATTERN.fullmatch(normalized):
            return "JWT_SECRET must be URL-safe base64 without padding"
        try:
            decoded = base64.urlsafe_b64decode(
                normalized + "=" * (-len(normalized) % 4)
            )
        except (binascii.Error, ValueError):
            return "JWT_SECRET must be valid URL-safe base64"
        if len(decoded) < 32:
            return "JWT_SECRET must decode to at least 32 bytes"

        counts = Counter(normalized)
        entropy = -sum(
            (count / len(normalized)) * math.log2(count / len(normalized))
            for count in counts.values()
        )
        if len(counts) < 16 or entropy < 4.0:
            return "JWT_SECRET lacks sufficient character diversity"
        if Settings._has_repeated_pattern(normalized):
            return "JWT_SECRET contains a periodic or repeated substring pattern"
        return None

    @staticmethod
    def _has_repeated_pattern(value: str) -> bool:
        """Detect full periodicity and non-overlapping repeated substrings."""
        length = len(value)
        for period in range(1, (length // 2) + 1):
            if all(
                value[index] == value[index % period] for index in range(period, length)
            ):
                return True

        for width in range(min(16, length // 2), 5, -1):
            first_position: dict[str, int] = {}
            for index in range(length - width + 1):
                block = value[index : index + width]
                previous = first_position.get(block)
                if previous is not None and index - previous >= width:
                    return True
                first_position.setdefault(block, index)
        return False

    def _validated_fcc_endpoint(self, value: str, name: str) -> str:
        try:
            parsed = urlsplit(value)
            port = parsed.port
        except ValueError as exc:
            raise ValueError(f"{name} contains an invalid port") from exc
        scheme = parsed.scheme.lower()
        if scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError(f"{name} must be an absolute HTTP(S) URL")
        if scheme == "http" and not self._cleartext_allowed(parsed.hostname):
            raise ValueError(
                f"{name} must use HTTPS unless its exact host is in INSECURE_INTERNAL_HOSTS"
            )
        if "*" in parsed.hostname:
            raise ValueError(f"{name} must name one explicit host")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError(f"{name} must not contain credentials")
        if parsed.fragment:
            raise ValueError(f"{name} must not contain a fragment")
        if parsed.query:
            raise ValueError(f"{name} must not contain a query string")

        try:
            address = ipaddress.ip_address(parsed.hostname)
        except ValueError:
            address = None
        if address and (
            address.is_loopback or address.is_private or address.is_link_local
        ):
            raise ValueError(
                f"{name} must not use a loopback, private, or link-local IP literal"
            )

        host = parsed.hostname.lower()
        if ":" in host:
            host = f"[{host}]"
        default_port = 443 if scheme == "https" else 80
        netloc = host if port in {None, default_port} else f"{host}:{port}"
        path = parsed.path or "/"
        return urlunsplit(SplitResult(scheme, netloc, path, "", ""))

    def _validate_shared_service_transports(self) -> list[str]:
        errors: list[str] = []

        try:
            database = make_url(self.resolved_database_url)
            if database.drivername.startswith("sqlite"):
                errors.append(
                    "DATABASE_URL must not use SQLite in a shared environment"
                )
            elif not database.drivername.startswith("postgresql"):
                errors.append(
                    "DATABASE_URL must use PostgreSQL in a shared environment"
                )
            else:
                sslmode_value = database.query.get("sslmode")
                sslmodes = (
                    sslmode_value
                    if isinstance(sslmode_value, tuple)
                    else (sslmode_value,)
                )
                tls_enforced = bool(sslmode_value) and all(
                    mode in {"require", "verify-full"} for mode in sslmodes
                )
                if not tls_enforced and not self._cleartext_allowed(database.host):
                    errors.append(
                        "external PostgreSQL requires sslmode=require or verify-full; cleartext requires its exact host in INSECURE_INTERNAL_HOSTS"
                    )
        except (ValueError, TypeError):
            errors.append("DATABASE_URL is not a valid SQLAlchemy database URL")

        try:
            redis = urlsplit(self.redis_url)
            _redis_port = redis.port
            if redis.scheme not in {"redis", "rediss"} or not redis.hostname:
                errors.append("REDIS_URL must be an absolute redis:// or rediss:// URL")
            elif redis.scheme == "redis" and not self._cleartext_allowed(
                redis.hostname
            ):
                errors.append(
                    "external Redis requires rediss://; cleartext requires its exact host in INSECURE_INTERNAL_HOSTS"
                )
        except ValueError:
            errors.append("REDIS_URL contains an invalid port")

        if self.otel_exporter_otlp_endpoint:
            try:
                otlp = urlsplit(self.otel_exporter_otlp_endpoint)
                _otlp_port = otlp.port
                if otlp.scheme not in {"http", "https"} or not otlp.hostname:
                    errors.append(
                        "OTEL_EXPORTER_OTLP_ENDPOINT must be an absolute HTTP(S) URL"
                    )
                elif otlp.scheme == "http" and not self._cleartext_allowed(
                    otlp.hostname
                ):
                    errors.append(
                        "external OTLP requires https://; cleartext requires its exact host in INSECURE_INTERNAL_HOSTS"
                    )
            except ValueError:
                errors.append("OTEL_EXPORTER_OTLP_ENDPOINT contains an invalid port")
        return errors

    @staticmethod
    def _validate_cors_origin(origin: str) -> None:
        try:
            parsed = urlsplit(origin)
            port = parsed.port
        except ValueError as exc:
            raise ValueError("CORS_ORIGINS contains an invalid port") from exc
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            raise ValueError("CORS_ORIGINS must contain only absolute HTTPS origins")
        if "*" in parsed.hostname:
            raise ValueError("CORS_ORIGINS must not contain wildcards")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("CORS_ORIGINS must not contain credentials")
        if parsed.path:
            raise ValueError("CORS_ORIGINS entries must not contain a path")
        if parsed.query or parsed.fragment:
            raise ValueError("CORS_ORIGINS must not contain query strings or fragments")
        canonical_host = parsed.hostname.lower()
        if ":" in canonical_host:
            canonical_host = f"[{canonical_host}]"
        canonical_netloc = (
            canonical_host if port in {None, 443} else f"{canonical_host}:{port}"
        )
        canonical = urlunsplit(SplitResult("https", canonical_netloc, "", "", ""))
        if origin != canonical:
            raise ValueError("CORS_ORIGINS entries must be canonical HTTPS origins")

    @model_validator(mode="after")
    def validate_shared_environment(self) -> "Settings":
        self.fcc_connector_mode = self.fcc_connector_mode.lower().strip()
        if self.fcc_connector_mode not in {"simulate", "network"}:
            raise ValueError("FCC_CONNECTOR_MODE must be 'simulate' or 'network'")

        if self.app_env not in {AppEnvironment.STAGING, AppEnvironment.PRODUCTION}:
            return self

        errors: list[str] = []
        errors.extend(self._validate_internal_host_allowlist())
        errors.extend(self._validate_shared_service_transports())
        secret_error = self._jwt_secret_error(self.jwt_secret)
        if secret_error:
            errors.append(secret_error)
        if self.demo_mode:
            errors.append("DEMO_MODE must be false")
        if self.fcc_connector_mode != "network":
            errors.append("FCC_CONNECTOR_MODE must be network")
        if not self.allowed_origins or "*" in self.allowed_origins:
            errors.append("CORS_ORIGINS must be a non-empty explicit allowlist")
        for origin in self.allowed_origins:
            try:
                self._validate_cors_origin(origin)
            except ValueError as exc:
                errors.append(str(exc))

        if not self.approved_fcc_endpoints:
            errors.append(
                "FCC_APPROVED_ENDPOINTS must explicitly allow the FCC endpoint"
            )
        else:
            try:
                configured_endpoint = self._validated_fcc_endpoint(
                    self.fcc_api_url, "FCC_API_URL"
                )
                approved_endpoints = {
                    self._validated_fcc_endpoint(endpoint, "FCC_APPROVED_ENDPOINTS")
                    for endpoint in self.approved_fcc_endpoints
                }
                if configured_endpoint not in approved_endpoints:
                    errors.append(
                        "FCC_API_URL must exactly match an FCC_APPROVED_ENDPOINTS entry"
                    )
            except ValueError as exc:
                errors.append(str(exc))

        if errors:
            raise ValueError(
                "unsafe shared-environment configuration: " + "; ".join(errors)
            )
        return self


settings = Settings()
