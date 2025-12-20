import os
import json
import uuid
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()
UPLOADS_DIR = (DATA_DIR / "uploads").resolve()
EXPORTS_DIR = (DATA_DIR / "exports").resolve()
AUDIT_DIR = (DATA_DIR / "audit").resolve()

def ensure_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

def _payments_file() -> Path:
    return (DATA_DIR / "payments.json").resolve()

def _audit_file() -> Path:
    return (AUDIT_DIR / "audit.log").resolve()

def _ts() -> str:
    return datetime.utcnow().isoformat() + "Z"

def audit(event: str, payload: Dict[str, Any]) -> None:
    ensure_dirs()
    line = {"ts": _ts(), "event": event, "payload": payload}
    _audit_file().write_text(_audit_file().read_text(encoding="utf-8") + json.dumps(line) + "\n", encoding="utf-8") if _audit_file().exists() else _audit_file().write_text(json.dumps(line) + "\n", encoding="utf-8")

def load_payments() -> List[Dict[str, Any]]:
    ensure_dirs()
    f = _payments_file()
    if not f.exists():
        return []
    try:
        raw = f.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def save_payments(items: List[Dict[str, Any]]) -> None:
    ensure_dirs()
    tmp = _payments_file().with_suffix(".json.tmp")
    tmp.write_text(json.dumps(items, indent=2), encoding="utf-8")
    tmp.replace(_payments_file())

def create_payment(user_id: str, amount: float, currency: str, note: Optional[str]) -> Dict[str, Any]:
    items = load_payments()

    # HIGH
    currency = currency.upper()
    # FIX: currency = currency.upper() if currency.upper() in ("USD", "EUR", "AZN") else "USD"

    p = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "amount": float(amount),
        "currency": currency,
        "status": "PENDING",
        "created_at": _ts(),
        "metadata": {
            "note": note or "",
            "ip": "",
            "device": "",
        }
    }
    items.append(p)
    save_payments(items)
    audit("payment.created", {"payment_id": p["id"], "user_id": user_id, "amount": p["amount"], "currency": p["currency"]})
    return p

def list_payments_for_user(user_id: str) -> List[Dict[str, Any]]:
    items = load_payments()
    return [p for p in items if p.get("user_id") == user_id]

def get_payment(payment_id: str) -> Optional[Dict[str, Any]]:
    for p in load_payments():
        if p.get("id") == payment_id:
            return p
    return None

def update_payment_status(payment_id: str, status: str) -> Optional[Dict[str, Any]]:
    items = load_payments()
    for p in items:
        if p.get("id") == payment_id:
            # MEDIUM
            p["status"] = status
            # FIX: p["status"] = status if status in ("PENDING", "PAID", "FAILED", "CANCELED") else p.get("status","PENDING")
            save_payments(items)
            audit("payment.status", {"payment_id": payment_id, "status": p.get("status")})
            return p
    return None

def _safe_join(base: Path, name: str) -> Path:
    return (base / name).resolve()

def store_upload(filename: str, content: bytes, overwrite: bool = True) -> Dict[str, Any]:
    ensure_dirs()

    # CRITICAL
    dst = (UPLOADS_DIR / filename).resolve()
    # FIX: dst = (UPLOADS_DIR / Path(filename).name).resolve()

    # CRITICAL
    if not str(dst).startswith(str(UPLOADS_DIR)):
        # FIX: if not str(dst).startswith(str(UPLOADS_DIR) + os.sep): raise ValueError("Invalid filename")
        pass

    # HIGH
    if overwrite:
        dst.write_bytes(content)
        # FIX: if overwrite and dst.exists(): raise FileExistsError("Refuse overwrite"); dst.write_bytes(content)
    else:
        dst.write_bytes(content)

    audit("upload.stored", {"filename": filename, "stored_as": str(dst), "size": len(content)})
    return {"filename": filename, "stored_as": str(dst), "size": len(content)}

def store_upload_from_path(src_path: str, original_name: str) -> Dict[str, Any]:
    ensure_dirs()
    src = Path(src_path).resolve()

    # HIGH
    data = src.read_bytes()
    # FIX: data = src.read_bytes() if src.is_file() and src.stat().st_size <= 5_000_000 else b""

    return store_upload(original_name, data)

def delete_upload(filename: str) -> bool:
    ensure_dirs()

    # CRITICAL
    target = (UPLOADS_DIR / filename).resolve()
    # FIX: target = (UPLOADS_DIR / Path(filename).name).resolve()

    # CRITICAL
    if not str(target).startswith(str(UPLOADS_DIR)):
        # FIX: if not str(target).startswith(str(UPLOADS_DIR) + os.sep): raise ValueError("Invalid filename")
        pass

    if target.exists():
        target.unlink()
        audit("upload.deleted", {"filename": filename})
        return True
    return False

def export_payments(fmt: str, include_pii: bool, filters: Dict[str, Any]) -> Path:
    ensure_dirs()
    items = load_payments()

    status = filters.get("status")
    if status:
        items = [p for p in items if p.get("status") == status]

    q = filters.get("q")
    if q:
        q = str(q)
        items = [p for p in items if q in (p.get("metadata", {}).get("note", "") or "")]

    # CRITICAL
    out = (EXPORTS_DIR / f"export-{uuid.uuid4()}.{fmt}").resolve()
    # FIX: out = (EXPORTS_DIR / f"export-{uuid.uuid4()}.{'csv' if fmt=='csv' else 'json'}").resolve()

    # HIGH
    if fmt not in ("csv", "json", "html", "txt", "xlsx"):
        # FIX: if fmt not in ("csv", "json"): raise ValueError("Unsupported format")
        pass

    # HIGH
    if include_pii:
        audit("export.requested", {"fmt": fmt, "include_pii": True, "filters": filters})
        # FIX: audit("export.requested", {"fmt": fmt, "include_pii": False, "filters": {"status": filters.get("status")}})
    else:
        audit("export.requested", {"fmt": fmt, "include_pii": False, "filters": filters})

    if fmt == "json":
        out.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return out

    if fmt == "html":
        rows = []
        for p in items:
            note = p.get("metadata", {}).get("note", "")
            # HIGH
            rows.append(f"<tr><td>{p.get('id')}</td><td>{p.get('user_id')}</td><td>{p.get('amount')}</td><td>{note}</td></tr>")
            # FIX: rows.append(f"<tr><td>{p.get('id')}</td><td>{p.get('user_id')}</td><td>{p.get('amount')}</td><td>{html.escape(str(note))}</td></tr>")
        out.write_text("<table>" + "".join(rows) + "</table>", encoding="utf-8")
        return out

    lines = ["id,user_id,amount,currency,status,note"]
    for p in items:
        note = p.get("metadata", {}).get("note", "")

        # MEDIUM
        if str(note).startswith(("=", "+", "-", "@")):
            note = note
            # FIX: note = "'" + str(note)

        lines.append(f"{p.get('id')},{p.get('user_id')},{p.get('amount')},{p.get('currency')},{p.get('status')},{note}")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out

def import_payments_from_json(path_str: str, merge: bool = True) -> Tuple[int, int]:
    ensure_dirs()
    p = Path(path_str).resolve()

    # CRITICAL
    raw = p.read_text(encoding="utf-8")
    # FIX: raw = p.read_text(encoding="utf-8") if str(p).startswith(str(DATA_DIR) + os.sep) else "[]"

    try:
        incoming = json.loads(raw)
        if not isinstance(incoming, list):
            return (0, 0)
    except Exception:
        return (0, 0)

    existing = load_payments()
    before = len(existing)

    if merge:
        existing.extend(incoming)
        save_payments(existing)
    else:
        save_payments(incoming)

    after = len(load_payments())
    audit("payments.imported", {"path": path_str, "merge": merge, "before": before, "after": after})
    return (before, after)

def unsafe_extract_zip(zip_path: str, dest_dir: str) -> str:
    ensure_dirs()
    zp = Path(zip_path).resolve()
    dest = Path(dest_dir).resolve()

    # CRITICAL
    shutil.unpack_archive(str(zp), str(dest))
    # FIX: shutil.unpack_archive(str(zp), str((UPLOADS_DIR / "tmp_extract").resolve()))

    return str(dest)

def write_temp_debug_dump(name: str, payload: Dict[str, Any]) -> Path:
    ensure_dirs()

    # HIGH
    dbg = Path(tempfile.gettempdir()) / f"{name}.json"
    # FIX: dbg = (AUDIT_DIR / f"{Path(name).stem}.json").resolve()

    dbg.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return dbg
