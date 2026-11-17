# KrishiInsights — System Architecture

This document describes the system architecture, component boundaries, data flow pipelines, and database design of the **KrishiInsights** platform.

---

## 1. Monorepo Architectural Overview

KrishiInsights adopts a modular monorepo pattern that cleanly separates the user interface, backend application programming interface, machine learning training workflows, database persistence, and canonical dataset tiers:

```
┌─────────────────────────────────────────────────────────────┐
│                   Next.js Frontend (UI)                     │
│  (App Router, React 19, TypeScript, Tailwind CSS, Recharts) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                       HTTP / JSON (REST)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend (API)                    │
│      (Routing, Pydantic Validation, Analytics Services)     │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
        SQL / Queries                 Pipeline Loading
               │                              │
┌──────────────▼──────────────┐ ┌─────────────▼───────────────┐
│     Neon Cloud Database     │ │   Trained Model Artifacts   │
│  (Serverless Postgres, AWS) │ │   (.joblib, Scikit-learn)   │
└──────────────▲──────────────┘ └─────────────▲───────────────┘
               │ Ingestion Pipeline           │ Feature Matrix
┌──────────────┴──────────────────────────────┴───────────────┐
│            Canonical Datasets (`datasets/`)                 │
│  ├── raw/ (agriculture/, rainfall/)                         │
│  ├── interim/                                               │
│  ├── processed/ (clean_crop_data.csv, combined_data.csv)    │
│  └── metadata/ (profiles, sources, codebooks)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Canonical Dataset Storage & Pipeline Flow

### 2.1 Storage Organization
* **Canonical Root (`datasets/`):** All agricultural and rainfall data is stored in the root `datasets/` directory.
* **No Redundant Copies:** The `ml/` module references `datasets/` directly via relative paths, eliminating duplicate files in `ml/data/` and preventing data drift.

### 2.2 Data Pipeline from Raw Source to PostgreSQL
```
[Official Sources: data.gov.in / NDAP / IMD]
                       │
                       ▼
         datasets/raw/crop_production.csv (15.3 MB)
         datasets/raw/rainfall.csv (524 KB)
                       │
                       ▼
         scripts/preprocess_data.py
         ├── Missing production filtering (1.52%)
         ├── Positive area verification (Area > 0)
         ├── Unit categorization (Coconut nuts vs. Field crop tonnes)
         ├── Yield derivation (Yield = Production / Area)
         └── Subdivision-to-State seasonal rainfall alignment
                       │
                       ▼
         datasets/processed/clean_crop_data.csv (242,296 rows)
         datasets/processed/combined_data.csv (242,296 rows)
                       │
                       ▼
         backend/app/services/ingestion_service.py
         ├── Reference caching (states, districts, crops)
         ├── Record validation & duplicate rejection
         └── Batch PostgreSQL ingestion (Alembic managed schema)
                       │
                       ▼
         Neon Serverless PostgreSQL (`neondb` on AWS us-east-1)
         (states, districts, crops, agricultural_records, rainfall_records)
```

---

## 3. Database Entity-Relationship Design

The relational schema is configured in `backend/app/models/agriculture.py` and versioned via Alembic migrations (`database/migrations/`):

1. **`states`:** Unique state registry (`id`, `state_name`, `source_code`).
2. **`districts`:** District records linked via `state_id` with cascading delete and composite uniqueness `(state_id, district_name)`.
3. **`crops`:** Normalized crop master table (`id`, `crop_name`, `crop_category`).
4. **`agricultural_records`:** Granular time-series observations linking `state_id`, `district_id`, `crop_id`, `season`, `year`, `area`, `production`, and `yield_amount`. Composite unique constraint prevents duplicate entries.
5. **`rainfall_records`:** Climate metrics linking `state_id`, `year`, `annual_rainfall_mm`, and seasonal totals (`monsoon_rainfall_mm`, `rabi_rainfall_mm`, `pre_monsoon_rainfall_mm`).
6. **`prediction_records`:** Historical query log storing `input_features` (JSON), `predicted_yield`, `model_name`, `model_version`, and `created_at`.

---

## 4. Component Boundaries & Responsibilities

### 4.1 Frontend (`frontend/`)
* Built with Next.js 16 (App Router), React 19, TypeScript, and Tailwind CSS.
* Communicates with the backend exclusively via standard HTTP REST endpoints.
* Houses reusable UI components (KPI cards, Recharts time-series trends, data explorer tables, and yield estimation form).

### 4.2 Backend API (`backend/`)
* Built with Python FastAPI, Pydantic, and SQLAlchemy 2.x.
* Connects to PostgreSQL using `psycopg2-binary` with connection pooling (`pool_pre_ping=True`).
* Provides decoupled environment configuration supporting both local development PostgreSQL and future hosted instances (Supabase, AWS RDS, Neon) without application code changes.
* Enforces CORS policies for `http://localhost:3000`.

### 4.3 Machine Learning & Analytics Module (`ml/`)
* Houses offline analytical engines (`ml/src/analytics/`), chart visualization tools (`ml/src/visualization/`), and automated test suites (`ml/tests/`).
* Directly queries Neon Serverless PostgreSQL (`neondb`) via `ml/src/database/connection.py` for all exploratory data analysis and aggregations.
* Houses executed programmatic Jupyter exploration notebooks (`ml/notebooks/01`–`05`).
* Serializes validated regression pipelines (`.joblib`) into `ml/artifacts/` for backend deployment.

---

## 5. Analytics & Visualization Pipeline Architecture (Stage 4)

Stage 4 established an end-to-end analytical computing layer decoupling database queries from presentation:

```
┌─────────────────────────────────────────────────────────────┐
│                 Neon PostgreSQL (`neondb`)                  │
│       agricultural_records (242k) | rainfall_records (3.7k) │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy Pooled / Unpooled
┌──────────────────────────────▼──────────────────────────────┐
│              `ml/src/database/connection.py`                │
│    Dialect Normalization, Engine Cache, Query Runners       │
└──────────────────────────────┬──────────────────────────────┘
                               │ DataFrames
┌──────────────────────────────▼──────────────────────────────┐
│                  `ml/src/analytics/`                        │
│  ├── agricultural_eda.py (Descriptive stats, annual trends) │
│  ├── crop_analysis.py    (Top-10 rankings, CV variability)  │
│  ├── regional_analysis.py(State performance, Shannon index) │
│  ├── rainfall_analysis.py(115-yr trends, LPA deviations)    │
│  ├── correlation_analysis(Seasonal, crop, state sensitivity)│
│  └── outlier_analysis.py (IQR, Z-score, anomaly classify)   │
└──────────────┬──────────────────────────────┬───────────────┘
               │ Analytical DataFrames        │ Validated Findings
┌──────────────▼──────────────┐ ┌─────────────▼───────────────┐
│   `ml/src/visualization/`   │ │       `ml/notebooks/`       │
│  (15 High-Res Figures)      │ │  (5 Executed Notebooks)     │
│  Saved in ml/reports/figures│ │  01_eda to 05_correlation   │
└─────────────────────────────┘ └─────────────────────────────┘
```

### Architectural Principles Applied in Stage 4:
1. **Mathematical Aggregate Yield:** All queries evaluate national/regional yield as $\frac{\sum \text{Production}}{\sum \text{Area}}$ to eliminate spatial weighting bias.
2. **Strict Unit Isolation:** Field crops ($\text{Tonnes/Ha}$) are never averaged with tree crops ($\text{Nuts/Ha}$).
3. **Composite Spatial Identity:** To prevent district name collisions, districts are queried and indexed as composite pairs `(state_name, district_name)`.
4. **Simpson's Paradox Resolution:** Cross-state spatial pooling is explicitly differentiated from within-state temporal sensitivity.
