# KrishiInsights — Agricultural Data Analytics & Crop Yield Intelligence Platform

> **Project Title:** KrishiInsights — An Agricultural Data Analytics and Crop Yield Intelligence Platform Using Machine Learning  
> **Academic Context:** Final-Year B.Tech Computer Science Project  
> **Current Status:** **Stage 3 Complete — Data Cleaning, Preprocessing & PostgreSQL Ingestion** (Database fully populated with 242,296 agricultural records, 3,772 rainfall records, 100% verified)

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
| **Database** | PostgreSQL 17, SQLAlchemy 2.x, Alembic 1.20 | Relational storage for structured agricultural and rainfall records |
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

1. Copy `.env.example` to `backend/.env` (or configure your environment variables):
   ```bash
   DATABASE_URL=postgresql+psycopg2://krishiinsights_user:<password>@localhost:5432/krishiinsights_db
   ```
2. Test database connectivity:
   ```bash
   python scripts/test_db_connection.py
   ```
3. Run schema migrations via Alembic:
   ```bash
   alembic upgrade head
   ```
4. Run dataset ingestion into PostgreSQL:
   ```bash
   # Run 1,000-row test and idempotency check
   python scripts/run_ingestion.py --test

   # Run full 242k-row ingestion
   python scripts/run_ingestion.py --full

   # Verify database metrics and referential integrity
   python scripts/run_ingestion.py --verify
   ```

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
> This repository is currently at **Stage 3 Complete (Data Cleaning, Preprocessing & Full PostgreSQL Ingestion)**. The canonical dataset tiers have been organized and profiled, the PostgreSQL 17 relational database has been migrated and fully populated with 242,296 agricultural records and 3,772 rainfall records, verified with 0 orphan records and 100% unit isolation. Stage 4 will cover Exploratory Data Analysis (EDA) and statistical distributions.
