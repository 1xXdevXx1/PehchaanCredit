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
| **Synthetic Dataset Generator** | **IMPLEMENTED** | Reproducible seed generator producing 1,000 vendors, 100k+ transactions, and repayment labels. |
| **Legacy Indices (FSI, TCI, BGI, FRI)** | **IMPLEMENTED** | Financial stability, transaction consistency, growth, and initial fraud risk. |
| **Framework Metrics (SPV, TSCI, MCS, Resilience)** | **IMPLEMENTED** | Supplier velocity (15%), business rhythm (15%), customer score (15%), STL seasonal resilience (10%). |
| **Hybrid Fraud & SVPS Engine** | **IMPLEMENTED** | Rules + Isolation Forest + NetworkX graph cycle detection ( \to B \to C \to A$) $\to$ SVPS $\in [0, 1]$. |
| **XGBoost Credit Quality ({base}$)** | **TRAINED** | XGBoost Regressor trained on behavioral signals (Test ^2 = 0.876$). |
| **SHAP Explainability** | **IMPLEMENTED** | Generates human-readable positive and negative factor attribution. |
| **Final Scoring & Decision Engine** | **IMPLEMENTED** | {final} = Q_{base} \times (1 - 0.25 \times \text{SVPS})$, $\text{Score} = 300 + 600 \times Q_{final}$, and underwriting actions. |
| **FastAPI REST Service** | **IMPLEMENTED** | Complete endpoint suite with automatic OpenAPI documentation. |
| **SQLite Database** | **IMPLEMENTED** | SQLAlchemy ORM tables seeded with 1,000 vendors and precomputed assessments. |
| **React Frontend** | **IMPLEMENTED** | Exact design, styles, responsive breakpoints, live API integration, and assessment modal. |
| **T-GAT + Time2Vec** | **OPTIONAL/EXPERIMENTAL** | Modular interface provided. Working demo runs on rules + Isolation Forest + NetworkX. |
| **Temporal Fusion Transformer (TFT)** | **OPTIONAL/NOT_TRAINED** | Modular architecture provided as research extension; demo uses trained XGBoost. |

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