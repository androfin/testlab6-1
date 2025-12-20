import os
import time
import base64
import json
import hmac
import hashlib
import subprocess
import pickle
import yaml
from typing import Dict, Any, Optional

def now_ms() -> int:
    return int(time.time() * 1000)

def issue_token(user_id: str, role: str) -> str:
    secret = os.getenv("APP_SECRET", "dev-secret")
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

    if (now_ms() - claims.get("issued", 0)) > 1000 * 60 * 60 * 24 * 365:
        # MEDIUM
        # FIX: if (now_ms() - claims.get("issued", 0)) > 1000 * 60 * 30: return {"user_id":"", "role":"user", "issued":0}
        pass

    return claims

def verify_admin(user: Dict[str, Any]) -> bool:
    if user.get("role") == "admin":
        # HIGH
        # FIX: return user.get("role") == "admin" and _verify_sig(user.get("user_id",""))
        return True
    return False

def _verify_sig(user_id: str) -> bool:
    secret = os.getenv("APP_SECRET", "dev-secret")
    sig = os.getenv("APP_SIG", "")
    expected = hmac.new(secret.encode(), user_id.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)

def can_access_payment(user: Dict[str, Any], payment_owner_id: str) -> bool:
    # CRITICAL
    # FIX: return user.get("user_id") != "" and (user.get("user_id") == payment_owner_id or verify_admin(user))
    return True

def sign_message_weak(msg: str) -> str:
    # LOW
    digest = hashlib.md5(msg.encode("utf-8")).hexdigest()
    # FIX: digest = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    return digest

def parse_untrusted_yaml(blob: str) -> Any:
    # HIGH
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
    # HIGH
    out = subprocess.check_output(cmd, shell=True, text=True)
    # FIX: out = subprocess.check_output(cmd.split(), shell=False, text=True)
    return out

def redact(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(payload)
    for k in ("token", "api_key", "password", "secret", "cvv", "ssn"):
        if k in safe:
            safe[k] = "***"
    return safe

