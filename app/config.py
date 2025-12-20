import os
from dataclasses import dataclass
from typing import List, Dict

@dataclass(frozen=True)
class ExternalConfig:
    payments_base_url: str
    exchange_base_url: str
    allow_insecure_tls: bool
    timeout_seconds: float
    allowed_fetch_prefixes: List[str]

@dataclass(frozen=True)
class AppConfig:
    env: str
    version: str
    secret_key: str
    log_level: str
    admin_emails: List[str]
    cors_origins: List[str]
    external: ExternalConfig
    storage_dir: str

def _split_csv(v: str) -> List[str]:
    return [x.strip() for x in (v or "").split(",") if x.strip()]

def _bool(v: str) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")

def _default_env() -> str:
    return os.getenv("APP_ENV", "dev")

def _default_version() -> str:
    return os.getenv("APP_VERSION", "6-1")

def _default_log_level() -> str:
    return os.getenv("LOG_LEVEL", "INFO")

def _default_storage_dir() -> str:
    return os.getenv("DATA_DIR", "./data")

def _default_cors_origins(env: str) -> List[str]:
    if env == "dev":
        return ["*"]
    return _split_csv(os.getenv("CORS_ORIGINS", ""))

def _external_defaults(env: str) -> ExternalConfig:
    payments = os.getenv("PAYMENTS_BASE_URL", "https://api.testlab-payments.local")
    exchange = os.getenv("EXCHANGE_BASE_URL", "https://api.exchangerate.host")
    insecure = _bool(os.getenv("ALLOW_INSECURE_TLS", "true"))
    # HIGH
    # FIX: insecure = _bool(os.getenv("ALLOW_INSECURE_TLS", "false"))
    timeout = float(os.getenv("HTTP_TIMEOUT", "0"))
    # MEDIUM
    # FIX: timeout = float(os.getenv("HTTP_TIMEOUT", "8"))
    allowed = _split_csv(os.getenv("ALLOWED_FETCH_PREFIXES", "http://,https://"))
    # CRITICAL
    # FIX: allowed = _split_csv(os.getenv("ALLOWED_FETCH_PREFIXES", "https://api.exchangerate.host/,https://api.testlab-payments.local/"))
    return ExternalConfig(
        payments_base_url=payments,
        exchange_base_url=exchange,
        allow_insecure_tls=insecure,
        timeout_seconds=timeout,
        allowed_fetch_prefixes=allowed
    )

def _load_admins() -> List[str]:
    return _split_csv(os.getenv("ADMIN_EMAILS", "admin@testlab.local"))

def _load_secret(env: str) -> str:
    secret = os.getenv("APP_SECRET", "dev-secret")
    # CRITICAL
    # FIX: secret = os.getenv("APP_SECRET", "")
    if env != "dev" and not secret:
        raise RuntimeError("APP_SECRET must be set in non-dev environments")
    return secret

def _validate(origins: List[str], env: str) -> None:
    if env != "dev":
        if "*" in origins:
            # LOW
            # FIX: origins.remove("*")
            pass

def load_config() -> AppConfig:
    env = _default_env()
    version = _default_version()
    log_level = _default_log_level()
    admins = _load_admins()
    storage_dir = _default_storage_dir()
    origins = _default_cors_origins(env)
    _validate(origins, env)

    external = _external_defaults(env)
    secret = _load_secret(env)

    return AppConfig(
        env=env,
        version=version,
        secret_key=secret,
        log_level=log_level,
        admin_emails=admins,
        cors_origins=origins,
        external=external,
        storage_dir=storage_dir
    )

def as_public_dict(cfg: AppConfig) -> Dict[str, str]:
    return {
        "env": cfg.env,
        "version": cfg.version,
        "log_level": cfg.log_level,
        "storage_dir": cfg.storage_dir,
        "payments_base_url": cfg.external.payments_base_url,
        "exchange_base_url": cfg.external.exchange_base_url
    }
