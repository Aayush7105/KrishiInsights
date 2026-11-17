# KrishiInsights — Agricultural Data Analytics & Crop Yield Intelligence Platform

> **Project Title:** KrishiInsights — An Agricultural Data Analytics and Crop Yield Intelligence Platform Using Machine Learning  
> **Academic Context:** Final-Year B.Tech Computer Science Project  
> **Current Status:** **Stage 4 Complete — Exploratory Data Analysis & Statistical Analysis** (Neon database analyzed across 242,296 agricultural and 3,772 rainfall records; 15 publication-grade figures, 5 executed notebooks, 6 comprehensive reports, 100% test coverage)

---

## 1. Project Overview & Objectives

**KrishiInsights** is a comprehensive web-based platform designed to analyze historical crop production, cultivated area, crop yield, and meteorological rainfall statistics across India's states and districts.

The platform's primary purpose is to empower researchers, policymakers, and agricultural stakeholders to explore and analyze agricultural records through interactive dashboards, multi-level geographic/temporal filters, and statistical insights. Machine learning serves as a supporting module to provide data-driven crop yield estimations under specified conditions.

### Core Objectives
1. **Historical Agricultural Analytics:** Explore and analyze historical crop production, cultivated area, and yield across India.
2. **Multi-dimensional Exploration:** Filter records across states, districts, crops, seasons (Kharif, Rabi, Summer, etc.), and harvest years.
3. **Comparative Analysis:** Compare agricultural efficiency across crops, seasons, and geographic regions.
4. **Rainfall & Meteorological Correlation:** Investigate historical precipitation patterns and evaluate statistical associations with crop yield.
5. **Interactive Statistical Visualizations:** Present descriptive statistics, trend lines, and distribution curves.
6. **Machine Learning Intelligence:** Provide regression-based crop yield estimation with documented accuracy metrics and honest caveats.
7. **Analytical Reports:** Export summary insights and reports.

---

## 2. Technology Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS | Responsive UI, interactive dashboards, dynamic routing |
| **Backend API** | Python 3.15, FastAPI, Pydantic | High-performance asynchronous REST API, validation, routing |
| **Database** | Neon Serverless PostgreSQL (AWS us-east-1), SQLAlchemy 2.x, Alembic 1.20 | Central cloud relational storage for agricultural and rainfall records |
| **Data & ML** | Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, Joblib | Data processing, statistical analytics, regression pipelines |
| **Tooling** | Git, Postman, ReportLab | Version control, endpoint testing, report generation |

---

## 3. Project Directory Structure

```text
KrishiInsights/
├── frontend/                     # Next.js TypeScript web application
│   ├── src/
│   │   └── app/
│   │       ├── layout.tsx        # Root layout with Tailwind CSS
│   │       ├── page.tsx          # Initial KrishiInsights landing view
│   │       └── globals.css       # Global styles
│   ├── package.json              # Frontend scripts & dependencies
│   ├── tsconfig.json             # TypeScript configuration (@/* alias)
│   └── next.config.ts            # Next.js runtime configuration
│
├── backend/                      # FastAPI Python REST API
│   ├── app/
│   │   ├── main.py               # FastAPI app & CORS configuration
│   │   ├── api/routes/health.py  # Health check endpoint (/api/health)
│   │   ├── core/config.py        # Environment & database configuration
│   │   ├── database/             # SQLAlchemy engine, session maker, and Base
│   │   ├── models/agriculture.py # Relational models (State, District, Crop, Records)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   └── services/             # Ingestion and analytics services
│   ├── tests/
│   │   ├── test_health.py        # Automated test suite for health endpoint
│   │   └── test_stage3_ingestion.py # Ingestion unit and database invariant tests
│   ├── requirements.txt          # Backend Python dependencies
│   └── .env                      # Local backend environment variables (git-ignored)
│
├── datasets/                     # Canonical Project Datasets
│   ├── raw/
│   │   ├── crop_production.csv   # Official crop production records (1997–2015, 246k rows)
│   │   └── rainfall.csv          # Official IMD rainfall records (1901–2015, 4.1k rows)
│   ├── processed/                # Validated clean crop & combined datasets (242k rows)
│   ├── metadata/                 # Profiling reports & source catalogues
│   └── README.md                 # Dataset documentation and codebook
│
├── ml/                           # Data Science & Machine Learning module
│   ├── data/                     # References canonical datasets/ via config
│   ├── notebooks/                # Jupyter EDA and model experiment notebooks
│   ├── src/                      # Feature engineering & ML scripts
│   ├── artifacts/                # Serialized model pipelines (.joblib)
│   └── requirements.txt          # ML-specific Python dependencies
│
├── database/                     # Relational database migrations & DDL
│   ├── migrations/               # Alembic versioned schema migrations
│   └── README.md                 # Database schema design & documentation
│
├── docs/                         # Project documentation
│   ├── ARCHITECTURE.md           # Monorepo architecture and component flow
│   ├── DATA_INGESTION_REPORT.md  # Stage 3 full ingestion and verification audit report
│   └── DEVELOPMENT_LOG.md        # Detailed chronological development diary
│
├── scripts/                      # Utility scripts (downloaders, preprocessors, verifiers)
│   ├── run_ingestion.py          # Data ingestion and verification CLI (--test, --full, --verify)
│   ├── preprocess_data.py        # Automated data cleaning & yield integration
│   ├── profile_datasets.py       # Dataset profiling script
│   └── test_db_connection.py     # Database connectivity testing script
│
├── alembic.ini                   # Alembic configuration pointing to database/migrations
├── .env.example                  # Environment variable template
├── .gitignore                    # Version control exclusion rules
├── CHANGELOG.md                  # Project versioning and milestone log
└── AGENTS.md                     # Permanent architectural rules and instructions
```

---

## 4. Official Data Sources & Coverage

* **Crop Production Statistics (1997–2015):** Directorate of Economics and Statistics (DES), Ministry of Agriculture and Farmers Welfare ([data.gov.in](https://www.data.gov.in/) & [NDAP, NITI Aayog](https://ndap.niti.gov.in/)). Covers 33 States/UTs, 646 Districts, 124 Crops.
* **Meteorological Precipitation (1901–2015):** India Meteorological Department ([IMD Mausam](https://mausam.imd.gov.in/)). Covers 36 Meteorological Subdivisions across India.

---

## 5. Database Configuration & Setup

1. Copy `.env.example` to `.env` and `backend/.env`:
   ```bash
   cp .env.example .env
   cp .env.example backend/.env
   ```
   Configure the shared Neon pooled and direct credentials (distributed securely out-of-band to teammates).
2. Test database connectivity against Neon:
   ```bash
   python scripts/test_neon_primary_app.py
   ```
3. Run schema migrations via Alembic (uses direct unpooled connection):
   ```bash
   alembic upgrade head
   ```
4. Verification & Audit Reports:
   ```bash
   # Run side-by-side local vs. Neon verification audit
   python scripts/verify_neon_migration.py
   ```
   See [docs/NEON_MIGRATION_REPORT.md](file:///d:/Major%20Project/docs/NEON_MIGRATION_REPORT.md) for complete forensic proof of 100% record and schema parity.

---

## 6. How to Run Frontend and Backend

### 6.1 Frontend (Next.js)
```bash
cd frontend
npm run dev
# Browser: http://localhost:3000
```

### 6.2 Backend (FastAPI)
```bash
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
# Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/api/health
```

---

## 7. Current Implementation Status

> [!NOTE]
> This repository is currently at **Stage 4 Complete (Exploratory Data Analysis & Statistical Analysis)**.
> All descriptive statistics, macro agricultural trends (1997–2015), 115-year IMD rainfall patterns (1901–2015), crop rankings, regional leaderboards across 33 states/UTs, paired seasonal correlations, and outlier analyses were computed directly from Neon PostgreSQL (`neondb`).
> Deliverables include 6 modular analytical engines (`ml/src/analytics/`), 15 publication-grade figures (`ml/reports/figures/`), 5 executed Jupyter notebooks (`ml/notebooks/`), 6 analytical markdown reports (`docs/`), and 11 automated pytest test cases (`ml/tests/test_analytics.py`) with 100% pass rate.
> Stage 5 will cover FastAPI backend development and analytics API implementation.
