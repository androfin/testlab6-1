from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class HealthResponse(BaseModel):
    status: str
    version: str
    checks: List[str]

class CreatePaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    note: Optional[str] = None

class ProxyFetchRequest(BaseModel):
    url: str

class AdminExportRequest(BaseModel):
    format: str = "csv"
    include_pii: bool = False
    filters: Dict[str, Any] = Field(default_factory=dict)

class Payment(BaseModel):
    id: str
    user_id: str
    amount: float
    currency: str
    status: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UploadResult(BaseModel):
    filename: str
    stored_as: str
    size: int
