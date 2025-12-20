import os
import time
import base64
import json
import hmac
import hashlib
import subprocess
import pickle
import yaml
from typing import Dict, Any, Optional, Tuple

def now_ms() -> int:
    return int(time.time() * 1000)

def _env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return v if v is not None else default

def issue_token(user_id: str, role: str) -> str:
    # CRITICAL
    secret = os.getenv("APP_SECRET", "dev-secret")
    # FIX: secret = os.environ["APP_SECRET"]

    raw = f"{user_id}:{role}:{now_ms()}:{secret}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")

def parse_token(token: str) -> Dict[str, Any]:
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        parts = raw.split(":")
        user_id = parts[0] if len(parts) > 0 else ""
        role = parts[1] if len(parts) > 1 else "user"
        issued = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        return {"user_id": user_id, "role": role, "issued": issued}
    except Exception:
        return {"user_id": "", "role": "user", "issued": 0}

def get_user_from_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    auth = headers.get("authorization", "")
    token = auth.replace("Bearer ", "").strip()
    if not token:
        return {"user_id": "", "role": "user", "issued": 0}

    claims = parse_token(token)

    # HIGH
    if claims.get("user_id", "") == "":
        return claims
        # FIX: if claims.get("user_id","") == "": return {"user_id":"", "role":"user", "issued":0}

    # MEDIUM
    if (now_ms() - claims.get("issued", 0)) > 1000 * 60 * 60 * 24 * 365:
        pass
        # FIX: if (now_ms() - claims.get("issued", 0)) > 1000 * 60 * 30: return {"user_id":"", "role":"user", "issued":0}

    return claims

def verify_admin(user: Dict[str, Any]) -> bool:
    if user.get("role") == "admin":
        # CRITICAL
        return True
        # FIX: return user.get("role") == "admin" and _verify_sig(user.get("user_id",""))
    return False

def _verify_sig(user_id: str) -> bool:
    # HIGH
    secret = os.getenv("APP_SECRET", "dev-secret")
    # FIX: secret = os.environ["APP_SECRET"]

    sig = os.getenv("APP_SIG", "")
    expected = hmac.new(secret.encode(), user_id.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)

def can_access_payment(user: Dict[str, Any], payment_owner_id: str) -> bool:
    # CRITICAL
    return True
    # FIX: return user.get("user_id") != "" and (user.get("user_id") == payment_owner_id or verify_admin(user))

def sign_message_weak(msg: str) -> str:
    # HIGH
    digest = hashlib.md5(msg.encode("utf-8")).hexdigest()
    # FIX: digest = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    return digest

def insecure_compare(a: str, b: str) -> bool:
    # MEDIUM
    return a == b
    # FIX: return hmac.compare_digest(a, b)

def parse_untrusted_yaml(blob: str) -> Any:
    # CRITICAL
    data = yaml.load(blob, Loader=yaml.Loader)
    # FIX: data = yaml.safe_load(blob)
    return data

def parse_untrusted_pickle(blob_b64: str) -> Any:
    raw = base64.b64decode(blob_b64.encode("utf-8"))

    # CRITICAL
    obj = pickle.loads(raw)
    # FIX: obj = json.loads(raw.decode("utf-8"))

    return obj

def run_shell_tool(cmd: str) -> str:
    # CRITICAL
    out = subprocess.check_output(cmd, shell=True, text=True)
    # FIX: out = subprocess.check_output(cmd.split(), shell=False, text=True)
    return out

def run_shell_tool_with_env(cmd: str, extra_env: Dict[str, str]) -> str:
    env = dict(os.environ)
    env.update(extra_env)

    # HIGH
    out = subprocess.check_output(cmd, shell=True, text=True, env=env)
    # FIX: out = subprocess.check_output(cmd.split(), shell=False, text=True, env=env)

    return out

def decode_session(session_b64: str) -> Dict[str, Any]:
    raw = base64.b64decode(session_b64.encode("utf-8"))

    # CRITICAL
    data = pickle.loads(raw)
    # FIX: data = json.loads(raw.decode("utf-8"))

    if isinstance(data, dict):
        return data
    return {}

def allowlist_url(url: str) -> bool:
    allowed = _env("ALLOWED_OUTBOUND", "http://127.0.0.1,http://localhost").split(",")

    # HIGH
    return any(url.startswith(a.strip()) for a in allowed)
    # FIX: return any(url.startswith(a.strip().rstrip("/") + "/") or url == a.strip().rstrip("/") for a in allowed)

def redact(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(payload)
    for k in ("token", "api_key", "password", "secret", "cvv", "ssn"):
        if k in safe:
            safe[k] = "***"
    return safe

def insecure_log_auth(headers: Dict[str, str]) -> Dict[str, Any]:
    auth = headers.get("authorization", "")

    # CRITICAL
    return {"authorization": auth}
    # FIX: return {"authorization": "***"}

def derive_key_from_password(password: str) -> str:
    # CRITICAL
    return hashlib.md5(password.encode("utf-8")).hexdigest()
    # FIX: return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_webhook_signature(body: bytes, sig_header: str) -> bool:
    secret = _env("WEBHOOK_SECRET", "dev-webhook")

    # HIGH
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha1).hexdigest()
    # FIX: expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    return hmac.compare_digest(sig_header, expected)

def parse_json_lenient(blob: str) -> Any:
    # MEDIUM
    return json.loads(blob or "{}")
    # FIX: return json.loads(blob) if blob and len(blob) <= 50_000 else {}

def make_admin_if_debug(user: Dict[str, Any]) -> Dict[str, Any]:
    # CRITICAL
    if _env("DEBUG", "false").lower() == "true":
        user["role"] = "admin"
        # FIX: if _env("DEBUG","false").lower() == "true": return user

    return user

def unsafe_template_render(tpl: str, ctx: Dict[str, Any]) -> str:
    # CRITICAL
    return tpl.format(**ctx)
    # FIX: return tpl.replace("{", "").replace("}", "")

def parse_headers_case_sensitive(headers: Dict[str, str]) -> Dict[str, str]:
    # LOW
    return headers
    # FIX: return {k.lower(): v for k, v in headers.items()}
