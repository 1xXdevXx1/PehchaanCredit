# PehchaanCredit — AI-Based Behavioral Trust Engine

> **AI-Based Behavioral Trust Engine for Credit Assessment of Street Vendors Using Digital Transaction Data**

---

## 1. Project Overview
PehchaanCredit is an explainable behavioral credit assessment prototype designed for informal street vendors who lack formal credit records or collateral. By evaluating UPI digital transaction flows, business rhythm, supplier velocity, customer diversity, seasonality, and fraud-aware synthetic volume penalties, it derives an explainable credit assessment and underwriter recommendation.

---

## 2. Architecture
`	ext
                    ┌─────────────────────────┐
                    │     React + Vite UI     │
                    │  (Preserved Exact CSS)  │
                    └────────────┬────────────┘
                                 │ REST API
                                 ▼
                    ┌─────────────────────────┐
                    │     FastAPI Backend     │
                    │  (Pydantic + CORS)      │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       ┌────────────┐    ┌──────────────┐    ┌──────────────┐
       │ Data Layer │    │ ML Pipeline  │    │ Database     │
       │ Pandas     │    │ XGBoost      │    │ SQLite       │
       │ Synthetic  │    │ Isolation    │    │ SQLAlchemy   │
       │ Generator  │    │   Forest     │    └──────────────┘
       └────────────┘    │ NetworkX     │
                         │ STL Season.  │
                         │ SHAP Expl.   │
                         │ Decision Eng │
                         └──────────────┘
`

---

## 3. Component Implementation Status

| Component | Status | Description |
| :--- | :--- | :--- |
| **Synthetic Dataset Generator** | **IMPLEMENTED** | Reproducible seed generator producing 1,000 realistic informal vendors, 100k+ multi-attributed transactions, and empirical repayment outcomes. |
| **Legacy Indices (FSI, TCI, BGI, FRI)** | **IMPLEMENTED** | Financial Stability Index, Transaction Consistency Index, Business Growth Index, and Fraud Risk Indicators. |
| **Novel Behavioral Metrics (SPV, TSCI, MCS, Resilience)** | **IMPLEMENTED** | Supplier Payment Velocity via circular time stats (15%), Transaction Stability via Shannon entropy (15%), Merchant Customer Score via reciprocity filtering (15%), and Weather-aware Seasonal Resilience (10%). |
| **Anti-Collusion & SVPS Graph Engine** | **IMPLEMENTED** | Multi-attributed NetworkX directed graph scanning for closed collusion loops ($A \to B \to C \to A$) with Reciprocal Amount Ratio ($\text{RAR} \ge 0.50$) yielding Synthetic Volume Penalty (SVPS). |
| **Credit Quality ML Model ($Q_{\text{base}}$)** | **TRAINED** | Supervised XGBoost Regressor trained on behavioral signals ($R^2 = 0.876$), predicting baseline unbanked creditworthiness. |
| **SHAP Explainability & Waterfall Statement** | **IMPLEMENTED** | RBI-compliant itemized factor attribution displaying transparent point-by-point adjustments from baseline to final score. |
| **Final Scoring & Decision Engine** | **IMPLEMENTED** | Calibrated composite formulation mapping to standard Indian credit bureau scale (300 to 900), paired with risk-banded underwriting and loan sizing actions. |
| **RBI Account Aggregator (AA) Service** | **IMPLEMENTED** | Mock consent artifact lifecycle (Active, 365-day validity, daily recurrent fetch) simulating encrypted bank transaction ingestion. |
| **FastAPI REST Service** | **IMPLEMENTED** | High-throughput asynchronous backend service with complete REST endpoints and automated OpenAPI/Swagger documentation. |
| **SQLite Database Layer** | **IMPLEMENTED** | SQLAlchemy ORM models managing 1,000 vendor profiles, transactions, AA consent records, and loan assessment applications. |
| **React + Vite Frontend** | **IMPLEMENTED** | Underwriter workspace dashboard featuring interactive portfolio inspection, Trust Assessment reports, quantile risk bands, and responsive design. |

---

## 4. Setup & Running Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ (Tested on Node v22.14.0)

### 1. Install Backend Dependencies
`ash
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r backend/requirements.txt
`

### 2. Generate Synthetic Dataset & Seed Database
`ash
python scripts/generate_data.py --vendors 1000 --months 6
python scripts/train_model.py
python scripts/seed_db.py
`

### 3. Start Backend Server
`ash
uvicorn backend.app.main:app --reload --port 8000
`
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 4. Start Frontend Application
`ash
cd frontend
npm install
npm run dev
`
- Access Web App: http://localhost:5173

### 5. Run Automated Test Suite
`ash
pytest
`

---

## 5. Limitations & Academic Disclaimer
- **Synthetic Dataset**: All transactions and repayment records are synthetically generated for prototype demonstration. Performance on synthetic data does not represent real-world lending validation.
- **Project-Defined Metric**: The generated Credit Score (300–900) is a project-defined behavioral estimate. It is **not** an official CIBIL, RBI, or banking credit bureau rating.
- **Prototype Scope**: Designed as an academic decision-support framework to demonstrate AI/ML behavioral trust modeling.