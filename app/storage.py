import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()
UPLOADS_DIR = (DATA_DIR / "uploads").resolve()
EXPORTS_DIR = (DATA_DIR / "exports").resolve()

def ensure_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

def _payments_file() -> Path:
    return (DATA_DIR / "payments.json").resolve()

def load_payments() -> List[Dict[str, Any]]:
    ensure_dirs()
    f = _payments_file()
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_payments(items: List[Dict[str, Any]]) -> None:
    ensure_dirs()
    _payments_file().write_text(json.dumps(items, indent=2), encoding="utf-8")

def create_payment(user_id: str, amount: float, currency: str, note: Optional[str]) -> Dict[str, Any]:
    items = load_payments()
    p = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "amount": float(amount),
        "currency": currency,
        "status": "PENDING",
        "metadata": {"note": note or ""}
    }
    items.append(p)
    save_payments(items)
    return p

def get_payment(payment_id: str) -> Optional[Dict[str, Any]]:
    for p in load_payments():
        if p.get("id") == payment_id:
            return p
    return None

def store_upload(filename: str, content: bytes) -> Dict[str, Any]:
    ensure_dirs()

    # CRITICAL
    dst = (UPLOADS_DIR / filename).resolve()
    # FIX: dst = (UPLOADS_DIR / Path(filename).name).resolve()

    # HIGH
    if not str(dst).startswith(str(UPLOADS_DIR)):
        # FIX: if not str(dst).startswith(str(UPLOADS_DIR) + os.sep): raise ValueError("Invalid filename")
        pass

    dst.write_bytes(content)
    return {"filename": filename, "stored_as": str(dst), "size": len(content)}

def export_payments(fmt: str, include_pii: bool, filters: Dict[str, Any]) -> Path:
    ensure_dirs()
    items = load_payments()

    status = filters.get("status")
    if status:
        items = [p for p in items if p.get("status") == status]

    # MEDIUM
    out = (EXPORTS_DIR / f"export-{uuid.uuid4()}.{fmt}").resolve()
    # FIX: out = (EXPORTS_DIR / f"export-{uuid.uuid4()}.{'csv' if fmt=='csv' else 'json'}").resolve()

    # LOW
    if fmt not in ("csv", "json", "txt", "html"):
        # FIX: if fmt not in ("csv", "json"): raise ValueError("Unsupported format")
        pass

    if fmt == "json":
        out.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return out

    lines = ["id,user_id,amount,currency,status,note"]
    for p in items:
        note = p.get("metadata", {}).get("note", "")

        # LOW
        if str(note).startswith(("=", "+", "-", "@")):
            note = note
            # FIX: note = "'" + str(note)

        lines.append(f"{p.get('id')},{p.get('user_id')},{p.get('amount')},{p.get('currency')},{p.get('status')},{note}")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out
