import hashlib
import uuid
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from backend.app.db.session import get_session
from backend.app.models.schemas import (
    User, UserCreate, UserLogin, Token,
    Product, ProductCreate,
    RiskAssessment, RiskAssessmentCreate,
    Certificate, CertificateCreateRequest, CertificateVerifyResponse,
    BlockchainBlock
)
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.services.iso_calculator import ISORiskCalculator
from backend.app.services.blockchain_ledger import BlockchainLedger
from backend.app.services.pdf_generator import PDFGenerator
from backend.app.services.external_api import ExternalAPIService

router = APIRouter()

# --- 1. AUTH ENDPOINTS ---
@router.post("/auth/register", response_model=User)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        company_name=user_in.company_name,
        role=user_in.role or "manufacturer"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/auth/login", response_model=Token)
def login(credentials: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == credentials.email)).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.email, "role": user.role})
    return Token(access_token=token, email=user.email, role=user.role)

# --- 2. DIRECTIVES & STANDARDS ---
@router.get("/directives")
def get_ce_directives():
    return [
        {"code": "2014/35/EU", "name": "Low Voltage Directive (LVD)", "standard": "EN 60335-1"},
        {"code": "2014/30/EU", "name": "Electromagnetic Compatibility (EMC)", "standard": "EN 55014-1"},
        {"code": "2006/42/EC", "name": "Machinery Directive (MD)", "standard": "EN ISO 12100:2010"},
        {"code": "2014/53/EU", "name": "Radio Equipment Directive (RED)", "standard": "EN 300 328"}
    ]

# --- 3. PRODUCTS ---
@router.post("/products", response_model=Product)
def create_product(product_in: ProductCreate, session: Session = Depends(get_session)):
    product = Product(
        name=product_in.name,
        model_number=product_in.model_number,
        category=product_in.category,
        manufacturer_id=1,
        description=product_in.description,
        serial_number=product_in.serial_number
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.get("/products", response_model=List[Product])
def get_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()

# --- 4. RISK ASSESSMENT (ISO 12100) ---
@router.post("/risk/calculate")
def calculate_and_save_risk(risk_in: RiskAssessmentCreate, session: Session = Depends(get_session)):
    init_calc = ISORiskCalculator.calculate_risk(risk_in.severity, risk_in.probability)
    res_calc = ISORiskCalculator.calculate_risk(risk_in.residual_severity, risk_in.residual_probability)
    
    risk_obj = RiskAssessment(
        product_id=risk_in.product_id,
        hazard_description=risk_in.hazard_description,
        severity=risk_in.severity,
        probability=risk_in.probability,
        initial_risk_score=init_calc["score"],
        mitigation_measures=risk_in.mitigation_measures,
        residual_severity=risk_in.residual_severity,
        residual_probability=risk_in.residual_probability,
        residual_risk_score=res_calc["score"],
        is_acceptable=res_calc["is_acceptable"]
    )
    session.add(risk_obj)
    session.commit()
    session.refresh(risk_obj)
    return {
        "risk_assessment_id": risk_obj.id,
        "initial": init_calc,
        "residual": res_calc,
        "status": "ISO 12100 Risk Evaluation Passed" if res_calc["is_acceptable"] else "Risk Unacceptable - Action Required"
    }

# --- 5. CERTIFICATE ISSUANCE & BLOCKCHAIN MINING ---
@router.post("/certificates/issue")
def issue_certificate(req: CertificateCreateRequest, session: Session = Depends(get_session)):
    product = session.get(Product, req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    user = session.get(User, product.manufacturer_id)
    company_name = user.company_name if user else "ACME Industrial Ltd."
    
    cert_uuid = str(uuid.uuid4())
    payload_string = f"{cert_uuid}:{product.id}:{product.serial_number}:{req.directive_code}"
    payload_hash = hashlib.sha256(payload_string.encode()).hexdigest()
    
    last_block = session.exec(select(BlockchainBlock).order_by(BlockchainBlock.block_index.desc())).first()
    prev_hash = last_block.block_hash if last_block else "0000000000000000000000000000000000000000000000000000000000000000"
    new_block_index = (last_block.block_index + 1) if last_block else 1
    
    block_data = BlockchainLedger.mine_block(
        index=new_block_index,
        previous_hash=prev_hash,
        cert_uuid=cert_uuid,
        payload_hash=payload_hash
    )
    
    block = BlockchainBlock(
        block_index=block_data["index"],
        timestamp=block_data["timestamp"],
        previous_hash=block_data["previous_hash"],
        certificate_uuid=cert_uuid,
        payload_hash=payload_hash,
        nonce=block_data["nonce"],
        block_hash=block_data["block_hash"]
    )
    session.add(block)
    
    pdf_filename = f"static/certificates/CE_Cert_{cert_uuid}.pdf"
    PDFGenerator.generate_ce_certificate(
        cert_uuid=cert_uuid,
        product_name=product.name,
        model_number=product.model_number,
        company_name=company_name,
        directive_code=req.directive_code,
        payload_hash=payload_hash,
        tx_hash=block_data["tx_hash"],
        output_path=pdf_filename
    )
    
    cert = Certificate(
        uuid=cert_uuid,
        product_id=product.id,
        directive_code=req.directive_code,
        status="ISSUED",
        pdf_path=pdf_filename,
        payload_hash=payload_hash,
        blockchain_tx_hash=block_data["tx_hash"],
        block_index=new_block_index
    )
    session.add(cert)
    session.commit()
    session.refresh(cert)
    
    return {
        "certificate_uuid": cert.uuid,
        "payload_hash": cert.payload_hash,
        "blockchain_tx_hash": cert.blockchain_tx_hash,
        "block_index": cert.block_index,
        "pdf_download_url": f"/{pdf_filename}",
        "message": "Certificate successfully generated and recorded to Blockchain Ledger!"
    }

# --- 6. PUBLIC BLOCKCHAIN VERIFICATION PORTAL API ---
@router.get("/verify/{certificate_uuid}", response_model=CertificateVerifyResponse)
def verify_certificate(certificate_uuid: str, session: Session = Depends(get_session)):
    cert = session.exec(select(Certificate).where(Certificate.uuid == certificate_uuid)).first()
    if not cert:
        return CertificateVerifyResponse(
            is_valid=False, status="INVALID", certificate_uuid=certificate_uuid,
            product_name="Unknown", company_name="Unknown", directive_code="Unknown",
            payload_hash="", blockchain_verified=False, block_index=0, blockchain_tx_hash="",
            created_at="", message="⚠️ CERTIFICATE NOT FOUND IN REGISTRY!"
        )
        
    product = session.get(Product, cert.product_id)
    user = session.get(User, product.manufacturer_id) if product else None
    
    block = session.exec(select(BlockchainBlock).where(BlockchainBlock.certificate_uuid == certificate_uuid)).first()
    blockchain_ok = block is not None and block.payload_hash == cert.payload_hash
    
    return CertificateVerifyResponse(
        is_valid=blockchain_ok,
        status="VERIFIED & IMMUTABLE" if blockchain_ok else "TAMPERED WARNING",
        certificate_uuid=cert.uuid,
        product_name=product.name if product else "N/A",
        company_name=user.company_name if user else "ACME Ltd.",
        directive_code=cert.directive_code,
        payload_hash=cert.payload_hash,
        blockchain_verified=blockchain_ok,
        block_index=cert.block_index,
        blockchain_tx_hash=cert.blockchain_tx_hash,
        created_at=str(cert.created_at),
        message="✅ Certificate authenticity verified on Blockchain Ledger." if blockchain_ok else "⚠️ SECURITY ALERT: Payload hash mismatch! This certificate or technical dossier has been ILLEGALLY TAMPERED WITH!"
    )

# --- 7. TAMPER SIMULATOR (SECURITY TEST ENDPOINT) ---
@router.post("/simulate-tamper/{certificate_uuid}")
def simulate_tamper(certificate_uuid: str, session: Session = Depends(get_session)):
    cert = session.exec(select(Certificate).where(Certificate.uuid == certificate_uuid)).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    # Tamper the hash in Database
    cert.payload_hash = "HACKED_FAKE_HASH_" + cert.payload_hash[:20]
    session.add(cert)
    session.commit()
    session.refresh(cert)
    return {
        "certificate_uuid": certificate_uuid,
        "tampered_hash": cert.payload_hash,
        "message": "ATTACK SIMULATED: Certificate payload hash in SQL DB has been corrupted! Test verification now."
    }

# --- 8. EXTERNAL API INTEGRATIONS ---
@router.get("/external/rates")
async def get_currency_rates():
    return await ExternalAPIService.fetch_currency_rates()

@router.get("/external/blockchain/{tx_hash}")
async def get_external_blockchain_info(tx_hash: str):
    return await ExternalAPIService.verify_polygon_block(tx_hash)
