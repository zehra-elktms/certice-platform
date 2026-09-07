import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.iso_calculator import ISORiskCalculator
from backend.app.services.blockchain_ledger import BlockchainLedger

client = TestClient(app)

def test_iso_calculator_acceptable_risk():
    result = ISORiskCalculator.calculate_risk(1, 2)
    assert result["score"] == 2
    assert result["risk_level"] == "LOW"
    assert result["is_acceptable"] is True

def test_iso_calculator_critical_risk():
    result = ISORiskCalculator.calculate_risk(5, 4)
    assert result["score"] == 20
    assert result["risk_level"] == "CRITICAL"
    assert result["is_acceptable"] is False

def test_blockchain_mining_integrity():
    block = BlockchainLedger.mine_block(
        index=1,
        previous_hash="00000000000000000000000000000000",
        cert_uuid="test-uuid-1234",
        payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    assert block["index"] == 1
    assert block["block_hash"].startswith("00")
    assert block["tx_hash"].startswith("0x")

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to CertiCE Platform API"
