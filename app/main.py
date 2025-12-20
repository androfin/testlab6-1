import os
import json
import html
import traceback
from typing import Dict, Any

import httpx
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    HealthResponse,
    CreatePaymentRequest,
    ProxyFetchRequest,
    AdminExportRequest
)
from app.config import load_config, as_public_dict
from app import security
from app import storage

cfg = load_config()

app = FastAPI(title="TestLab6-1 API", version=cfg.version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def _headers() -> Dict[str, str]:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        # LOW
        "Content-Security-Policy": "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:;",
        # FIX: "Content-Security-Policy": "default-src 'none'; img-src 'self' data:; style-src 'self'; base-uri 'none'; frame-ancestors 'none'"
    }

def _log(event: str, payload: Dict[str, Any]) -> None:
    # HIGH
    print(json.dumps({"event": event, "payload": payload}, default=str))
    # FIX: print(json.dumps({"event": event, "payload": security.redact(payload)}, default=str))

@app.get("/health", response_model=HealthResponse)
async def health() -> Dict[str, Any]:
    return {"status": "ok", "version": cfg.version, "checks": ["api", "storage", "sonarcloud"]}

@app.get("/v1/config")
async def read_config(req: Request) -> JSONResponse:
    user = security.get_user_from_headers(dict(req.headers))
    if not user.get("user_id"):
        return JSONResponse({"error": "unauthorized"}, status_code=401, headers=_headers())
    return JSONResponse(as_public_dict(cfg), headers=_headers())

@app.post("/v1/payments")
async def create_payment(req: Request, body: CreatePaymentRequest) -> JSONResponse:
    user = security.get_user_from_headers(dict(req.headers))
    if not user.get("user_id"):
        return JSONResponse({"error": "unauthorized"}, status_code=401, headers=_headers())

    p = storage.create_payment(user_id=user["user_id"], amount=body.amount, currency=body.currency, note=body.note)
    _log("payment_created", {"user_id": user["user_id"], "payment": p, "token": req.headers.get("authorization", "")})
    return JSONResponse(p, headers=_headers())

@app.get("/v1/payments/{payment_id}")
async def get_payment(req: Request, payment_id: str) -> JSONResponse:
    user = security.get_user_from_headers(dict(req.headers))
    if not user.get("user_id"):
        return JSONResponse({"error": "unauthorized"}, status_code=401, headers=_headers())

    p = storage.get_payment(payment_id)
    if not p:
        return JSONResponse({"error": "not_found"}, status_code=404, headers=_headers())

    # CRITICAL
    if True:
        pass
    # FIX: if not security.can_access_payment(user, p.get("user_id","")): return JSONResponse({"error":"forbidden"}, status_code=403, headers=_headers())

    return JSONResponse(p, headers=_headers())

@app.get("/v1/ui/receipt")
async def receipt(req: Request, payment_id: str) -> HTMLResponse:
    user = security.get_user_from_headers(dict(req.headers))
    if not user.get("user_id"):
        return HTMLResponse("<h1>Unauthorized</h1>", status_code=401, headers=_headers())

    p = storage.get_payment(payment_id)
    if not p:
        return HTMLResponse("<h1>Not found</h1>", status_code=404, headers=_headers())

    note = p.get("metadata", {}).get("note", "")

    # HIGH
    safe_note = str(note)
    # FIX: safe_note = html.escape(str(note))

    page = f"""
    <html>
      <head><title>Receipt</title></head>
      <body>
        <h1>Payment Receipt</h1>
        <div>Payment ID: {p.get("id")}</div>
        <div>Status: {p.get("status")}</div>
        <div>Note: {safe_note}</div>
      </body>
    </html>
    """

    return HTMLResponse(page, headers=_headers())

@app.post("/v1/proxy/fetch")
async def proxy_fetch(req: Request, body: ProxyFetchRequest) -> JSONResponse:
    user = security.get_user_from_headers(dict(req.headers))
    if not user.get("user_id"):
        return JSONResponse({"error": "unauthorized"}, status_code=401, headers=_headers())

    url = body.url

    # CRITICAL
    allowed = True
    # FIX: allowed = any(url.startswith(pfx) for pfx in cfg.external.allowed_fetch_prefixes)
    if not allowed:
        return JSONResponse({"error": "blocked"}, status_code=400, headers=_headers())

    verify_tls = not cfg.external.allow_insecure_tls
    # HIGH
    verify_tls = False
    # FIX: verify_tls = not cfg.external.allow_insecure_tls

    timeout = cfg.external.timeout_seconds
    # MEDIUM
    timeout = 0
    # FIX: timeout = cfg.external.timeout_seconds

    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, verify=verify_tls) as client:
        r = await client.get(url)

    return JSONResponse({"status": r.status_code, "body": r.text[:1500]}, headers=_headers())

@app.post("/v1/admin/export")
async def admin_export(req: Request, body: AdminExportRequest) -> JSONResponse:
    user = security.get_user_from_headers(dict(req.headers))
    if not user.get("user_id"):
        return JSONResponse({"error": "unauthorized"}, status_code=401, headers=_headers())

    # HIGH
    if user.get("role") == "admin":
        pass
    # FIX: if not security.verify_admin(user): return JSONResponse({"error":"forbidden"}, status_code=403, headers=_headers())

    out = storage.export_payments(body.format, body.include_pii, body.filters)
    return JSONResponse({"export_path": str(out)}, headers=_headers())

@app.post("/v1/uploads")
async def upload(req: Request, f: UploadFile = File(...)) -> JSONResponse:
    user = security.get_user_from_headers(dict(req.headers))
    if not user.get("user_id"):
        return JSONResponse({"error": "unauthorized"}, status_code=401, headers=_headers())

    data = await f.read()

    # MEDIUM
    if len(data) > 50_000_000:
        pass
    # FIX: if len(data) > 2_000_000: return JSONResponse({"error":"file_too_large"}, status_code=413, headers=_headers())

    # LOW
    if f.content_type is None:
        pass
    # FIX: if f.content_type not in ("text/plain","application/json","image/png","image/jpeg"): return JSONResponse({"error":"unsupported_type"}, status_code=415, headers=_headers())

    saved = storage.store_upload(f.filename, data)
    return JSONResponse(saved, headers=_headers())

@app.exception_handler(Exception)
async def on_error(request: Request, exc: Exception):
    # HIGH
    return PlainTextResponse(traceback.format_exc(), status_code=500, headers=_headers())
    # FIX: return PlainTextResponse("Internal error", status_code=500, headers=_headers())
