from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

# --- SQLModel Tabloları ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    company_name: str
    role: str = Field(default="manufacturer")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    model_number: str
    category: str
    manufacturer_id: int = Field(foreign_key="user.id")
    description: str
    serial_number: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RiskAssessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    hazard_description: str
    severity: int
    probability: int
    initial_risk_score: int
    mitigation_measures: str
    residual_severity: int
    residual_probability: int
    residual_risk_score: int
    is_acceptable: bool = Field(default=True)

class Certificate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)
    product_id: int = Field(foreign_key="product.id")
    directive_code: str
    status: str = Field(default="ISSUED")
    pdf_path: str = Field(default="")
    payload_hash: str = Field(index=True)
    blockchain_tx_hash: str = Field(default="")
    block_index: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BlockchainBlock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    block_index: int = Field(index=True)
    timestamp: float
    previous_hash: str
    certificate_uuid: str
    payload_hash: str
    nonce: int
    block_hash: str

# --- API İstek/Yanıt Şemaları ---

class UserCreate(BaseModel):
    email: str
    password: str
    company_name: str
    role: Optional[str] = "manufacturer"

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    role: str

class ProductCreate(BaseModel):
    name: str
    model_number: str
    category: str
    description: str
    serial_number: str

class RiskAssessmentCreate(BaseModel):
    product_id: int
    hazard_description: str
    severity: int
    probability: int
    mitigation_measures: str
    residual_severity: int
    residual_probability: int

class CertificateCreateRequest(BaseModel):
    product_id: int
    directive_code: str

class CertificateVerifyResponse(BaseModel):
    is_valid: bool
    status: str
    certificate_uuid: str
    product_name: str
    company_name: str
    directive_code: str
    payload_hash: str
    blockchain_verified: bool
    block_index: int
    blockchain_tx_hash: str
    created_at: str
    message: str
