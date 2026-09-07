# CertiCE — Enterprise CE Certification & Blockchain Verification Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Blockchain](https://img.shields.io/badge/Blockchain-SHA256_Ledger-F7931A?style=for-the-badge&logo=bitcoin&logoColor=white)](https://en.wikipedia.org/wiki/Blockchain)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

CertiCE is an enterprise-grade digital certification and compliance platform designed to automate European Union (EU) CE conformity assessments, EN ISO 12100 risk evaluations, dynamic QR-coded PDF Declaration of Conformity issuance, and cryptographic SHA-256 Blockchain Ledger verification to prevent document tampering.

---

## Key Features

- EN ISO 12100 Risk Assessment Engine: Automatically calculates initial and residual risk scores based on severity and probability metrics.
- SHA-256 Cryptographic Blockchain Ledger: Implements a Proof-of-Work immutability ledger to record certificate payloads and prevent database/PDF tampering.
- Automated Declaration of Conformity (DoC) PDF Generator: Generates official PDF certificates embedded with dynamic verification QR codes using ReportLab.
- Public Blockchain Verification Portal: Allows auditors and customs inspectors to verify certificate integrity by scanning QR codes or querying certificate UUIDs.
- Tamper Attack Simulator: Includes an interactive security test endpoint and frontend UI control to demonstrate real-time hash mismatch detection.
- Asynchronous External API Integration: Utilizes async HTTPX clients to interact with Polygon Blockchain Explorer services and live European currency conversion rates.
- Automated Test Suite: Includes comprehensive unit and integration tests using Pytest.

---

## System Architecture

```text
[ Client (Frontend SPA) ]
           │
           ▼ (Async REST API / HTTP)
[ FastAPI Backend Application ] ──► [ EN ISO 12100 Risk Engine ]
           │                     ──► [ SHA-256 Blockchain Ledger & Tamper Detection ]
           │                     ──► [ ReportLab PDF & QR Engine ]
           ▼
[ SQLite / SQLModel Database ] ──► [ External Polygon & Currency APIs ]
```

---

## Technical Stack

- Backend Framework: FastAPI (Python 3.10+)
- ORM & Database: SQLModel, SQLAlchemy, SQLite
- Cryptography & Blockchain: SHA-256 Hashing, Custom Proof-of-Work Mining Engine
- PDF & Media Generation: ReportLab, QRCode, Pillow
- External Requests: HTTPX Async Client
- Authentication & Security: Passlib (Bcrypt), PyJWT
- Testing Framework: Pytest, Pytest-Asyncio
- Frontend: HTML5, CSS3 (Glassmorphism Dark Mode), Vanilla JavaScript

---

## Project Structure

```text
certice-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # REST API endpoints (auth, products, risk, certificates, verify, tamper-simulator)
│   │   ├── core/         # Settings, JWT security configuration
│   │   ├── db/           # Database engine & session management
│   │   ├── models/       # SQLModel entities & Pydantic schemas
│   │   └── services/     # Risk calculator, Blockchain ledger, PDF generator, External APIs
│   └── tests/            # Automated Pytest test suite
├── frontend/             # Single Page Application (UI & Public Verifier)
├── static/               # Generated PDF certificates
├── README.md
└── requirements.txt
```

---

## Installation & Setup Guide

### 1. Prerequisites & Virtual Environment

Ensure Python 3.10+ is installed on your system.

```bash
git clone https://github.com/YOUR_USERNAME/certice-platform.git
cd certice-platform
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Backend Server

```bash
python3 -m uvicorn backend.app.main:app --reload --port 8000
```

Access Interactive OpenAPI Documentation at: http://127.0.0.1:8000/docs

### 4. Run Frontend Application

In a separate terminal window:

```bash
python3 -m http.server 3000 --directory frontend
```

Access User Interface at: http://127.0.0.1:3000

### 5. Execute Automated Tests

```bash
python3 -m pytest backend/tests/test_main.py
```

---

## License

Distributed under the MIT License.
