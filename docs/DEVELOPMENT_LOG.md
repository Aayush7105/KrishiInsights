# KrishiInsights — Development Log

This document serves as the chronological developer diary for the **KrishiInsights** project, detailing technical decisions, commands executed, test results, and notes for student developers.

---

## Session: 2026-11-17 — Stage 1: Project Initialization & Environment Setup

### 1. Objective
Establish the foundational monorepo structure, development environment, and initial verifiable skeletons for the Next.js frontend and FastAPI backend without implementing business logic or application features prematurely.

---

### 2. Environment Inspection
* **Operating System:** Windows 11
* **Node.js:** v24.18.0
* **npm:** 11.16.0
* **Python:** 3.15.2 (64-bit)
* **Git:** Initialized repository on branch `main`
* **PostgreSQL:** Service not currently installed locally. Relational connection will be configured via managed/containerized instance or local service during Stage 2 & 3.

---

### 3. Directories & Files Created

#### Monorepo Root:
* `AGENTS.md`: Permanent architecture and operational rules for the project.
* `README.md`: Central documentation, prerequisites, and execution commands.
* `CHANGELOG.md`: Chronological log of changes.
* `.env.example`: Template for environment variables (`DATABASE_URL`, `NEXT_PUBLIC_API_URL`).
* `.gitignore`: Excludes caches, virtual environments, build artifacts, and secrets while preserving `.env.example`.

#### Frontend (`frontend/`):
* `src/app/layout.tsx`: Root layout with font and metadata.
* `src/app/page.tsx`: Initial verified landing page identifying KrishiInsights.
* `src/app/globals.css`: Base Tailwind CSS styles.
* `tsconfig.json`: TypeScript configuration with `@/*` mapped to `./src/*`.
* `next.config.ts`: Clean Next.js configuration.
* `package.json`: Frontend scripts and dependencies.

#### Backend (`backend/`):
* `app/main.py`: FastAPI application initialization with CORS middleware.
* `app/core/config.py`: Application settings and CORS allowed origins.
* `app/api/routes/health.py`: `GET /api/health` endpoint with status and ISO timestamp.
* `tests/test_health.py`: Automated test validating health endpoint and route registration.
* `requirements.txt`: Minimal backend runtime dependencies (`fastapi`, `uvicorn`, `pydantic`).
* `.env`: Local environment settings for backend.

#### Machine Learning (`ml/`):
* `data/raw/`, `data/interim/`, `data/processed/`: Standard data science tier directories.
* `notebooks/`: Directory for Jupyter EDA notebooks.
* `src/data/`, `src/features/`, `src/models/`, `src/visualization/`: Modular ML scripts.
* `artifacts/`, `reports/`: Serialized models and evaluation outputs.
* `requirements.txt`: Data science dependencies (`pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `joblib`, `jupyter`).
* `README.md`: Explains ML environment isolation and model promotion workflow.

#### Database (`database/`):
* `migrations/`: Directory for versioned Alembic schema migrations.
* `README.md`: Explains PostgreSQL integration and planned relational entities.

---

### 4. Technical Decisions & Rationales (Student Developer Notes)

1. **Why Separate Backend and ML Dependency Files?**
   * *Rationale:* Machine learning training requires heavy libraries (`scikit-learn`, `matplotlib`, `seaborn`, `jupyter`), which are unnecessary for running the web API in production. By maintaining `backend/requirements.txt` separate from `ml/requirements.txt`, the API service stays lean, fast-starting, and lightweight.

2. **Why Use Next.js App Router with `src/`?**
   * *Rationale:* The `src/` directory pattern cleanly isolates application source code from configuration files at the root (`package.json`, `tsconfig.json`, `tailwind.config.ts`), preventing clutter and making path aliases (`@/components`, `@/lib`) intuitive.

3. **CORS (Cross-Origin Resource Sharing) Configuration:**
   * *Rationale:* The Next.js frontend runs on `http://localhost:3000` while the FastAPI backend runs on `http://localhost:8000`. By configuring `CORSMiddleware` in FastAPI on day one, browser requests from the frontend to the backend will not be blocked by cross-origin security restrictions.

4. **Synchronous vs Asynchronous Health Check:**
   * *Rationale:* For lightweight in-memory checks like `GET /api/health` that perform no I/O, a synchronous route function executes with zero event-loop overhead and is straightforward to unit test directly without async test runners.

---

### 5. Verification Commands & Results

| Step | Command Executed | Result | Status |
| :--- | :--- | :--- | :--- |
| **Frontend Build** | `cd frontend && npx next build` | Compiled successfully in 434ms; 4/4 static pages generated with 0 errors | **PASSED** |
| **Backend Route & Health Test** | `python backend/tests/test_health.py` | Health endpoint returned status `healthy`; OpenAPI route registration verified | **PASSED** |
| **Uvicorn Import Check** | `python -c "import uvicorn; from app.main import app"` | Uvicorn successfully loaded `app.main:app` | **PASSED** |

---

### 6. Known Limitations & Next Steps
* PostgreSQL database instance needs to be provisioned (local or containerized) when moving into Stage 2 (Dataset Research, Acquisition & Database Design).
* No application features (charts, filters, predictions) have been built yet, strictly adhering to Stage 1 constraints.


---

## Session: 2026-11-17 — Stage 1 Final Verification & Quality Audit

### 1. Verification Scope
* Python compatibility assessment for data/ML stack.
* Git status and repository integrity audit.
* Dataset directory organization evaluation (`datasets/` vs `ml/data/`).
* Frontend production build re-test and backend health check re-test.
* Documentation synchronization check.

### 2. Python Compatibility Evaluation
* **Installed Version:** Python 3.15.2 (64-bit on Windows)
* **Package Status:** `fastapi` (0.163.1), `uvicorn` (0.54.0), `pydantic` (2.14.3), `pandas` (3.1.1), `numpy` (2.5.5), `scikit-learn` (1.9.1), `joblib` (1.6.0), `sqlalchemy` (2.1.8) are pre-installed, functional, and verified.
* **Compatibility Analysis:**
  - In local development on this machine, all core packages function properly.
  - However, for cross-platform team reproducibility and production containerization/deployment (e.g. Docker, Render, AWS), Python 3.11 or 3.12 is the officially recommended standard LTS version due to pre-compiled wheel stability across Linux/cloud hosts.
  - Recommendation: Maintain the existing local Python 3.15 environment without disruption for current development, while specifying Python 3.11/3.12 in deployment configurations (`runtime.txt`, `Dockerfile`) for production parity.

### 3. Git & File Integrity Findings
* `git status` reports working tree completely clean.
* Pre-existing Next.js code was moved cleanly to `frontend/` with zero data loss.
* No useful user work was removed or lost.
* Environment variables and secrets (`backend/.env`) are properly excluded from version control while preserving `.env.example`.

### 4. Dataset Directory Organization Assessment
* **Current State:** Datasets exist in both `datasets/` and `ml/data/` (71 MB each, 142 MB total).
* **Evaluation:**
  - `datasets/`: Monorepo root convention, accessible to backend database ingestion and root documentation.
  - `ml/data/`: Data science tiered convention (`raw/`, `interim/`, `processed/`).
* **Recommendation:** Standardize on `ml/data/` as the single canonical data location for all data science operations, with symbolic links or direct path configuration for backend database seed scripts, eliminating 71 MB of redundant duplicate tracking in Git. Files preserved pending user approval.

### 5. Final Test Results
* `python backend/tests/test_health.py`: **PASSED** (Exit code 0, health endpoint and OpenAPI paths verified).
* `cd frontend && npx next build`: **PASSED** (Exit code 0, 4/4 static pages prerendered successfully with zero errors).


---

## Session: 2026-11-17 — Stage 2: Dataset Research, Acquisition, and Database Design

### 1. Objective
Establish an authentic agricultural and rainfall dataset foundation, perform data profiling, enforce canonical dataset organization, design a PostgreSQL relational schema reflecting real dataset structures, apply Alembic migrations, and prepare ingestion foundations without starting application feature development prematurely.

---

### 2. Dataset Research & Selection Evaluation

* **Selected Agricultural Dataset:**
  - *Title:* Crop Production in India (1997–2015).
  - *Authority:* Directorate of Economics & Statistics (DES), Ministry of Agriculture & Farmers Welfare, Government of India.
  - *Portals:* [data.gov.in](https://www.data.gov.in/) & [NDAP (NITI Aayog)](https://ndap.niti.gov.in/).
  - *Coverage:* 33 States/UTs, 646 Districts, 124 Crops, 1997–2015 (246,091 records).
  - *Selection Rationale:* Highest spatial granularity (district-level), comprehensive multi-season tracking (`Kharif`, `Rabi`, `Summer`, `Autumn`, `Winter`), and official government lineage.
* **Selected Meteorological Dataset:**
  - *Title:* Subdivision-wise Historical Rainfall (1901–2015).
  - *Authority:* India Meteorological Department (IMD), Ministry of Earth Sciences.
  - *Portals:* [mausam.imd.gov.in](https://mausam.imd.gov.in/) & data.gov.in.
  - *Coverage:* 36 Meteorological Subdivisions, 1901–2015, monthly & seasonal precipitation (4,116 records).
  - *Selection Rationale:* Official meteorological authority in India, contiguous historical timeline overlapping 100% of the crop production dataset years (1997–2015).
* **Rejected Data Sources:**
  - Synthetic / Mock Kaggle datasets lacking government provenance.
  - Station-level daily precipitation datasets (unnecessary gigabyte overhead for annual/seasonal crop yield modeling at this stage).

---

### 3. Canonical Dataset Storage Reorganization

* **Hash Verification:** Verified SHA-256 checksums across `datasets/` and `ml/data/` (100% identical byte-for-byte content).
* **Canonical Directory:** Restructured root `datasets/` as the single canonical location:
  - `datasets/raw/agriculture/crop_production.csv` (15.3 MB)
  - `datasets/raw/rainfall/rainfall.csv` (524 KB)
  - `datasets/processed/clean_crop_data.csv` (22.6 MB, 242,296 records)
  - `datasets/processed/combined_data.csv` (32.8 MB, 242,296 records)
  - `datasets/metadata/` (JSON profiling reports & Markdown data dictionary)
* **ML Deduplication:** Removed duplicate 71 MB files from `ml/data/`, replacing them with `ml/data/README.md` directing ML pipelines to read from `datasets/`.

---

### 4. Data Quality & Profiling Findings

Executed `scripts/profile_datasets.py`:
1. **Missing Production:** 3,730 records (1.52%) in raw crop data had null production values and were excluded from yield calculation.
2. **Cultivated Area Integrity:** Filtered non-positive area records (`Area <= 0`) to prevent division by zero in yield derivation ($\text{Yield} = \text{Production} / \text{Area}$).
3. **Unit Distinction (Coconut Anomaly):** Coconut production is officially reported in **Number of Nuts** (median ~239,000 nuts), while field crops are reported in **Metric Tonnes**. Handled by explicit unit columns (`Production_Unit`, `Yield_Unit`).
4. **Spatial Aggregation:** IMD's 36 subdivisions were mapped deterministically to 33 states/UTs to enable clean state-level integration without creating false district-level claims.

---

### 5. PostgreSQL Database Design & Migration

* **Configuration:**
  - Local database: `krishiinsights_db`, user: `krishiinsights_user`, port: `5432`.
  - Credentials stored safely in `backend/.env` (excluded from Git).
  - Portability: `DATABASE_URL` is environment-driven, enabling seamless transition to hosted cloud instances (Supabase, Neon, AWS RDS) without code changes.
* **SQLAlchemy Models (`backend/app/models/agriculture.py`):**
  - `State`, `District`, `Crop`, `AgriculturalRecord`, `RainfallRecord`, `PredictionRecord`.
  - Enforced foreign keys, cascading constraints, and composite uniqueness (`uq_state_district`, `uq_agri_record`, `uq_state_year_rainfall`).
* **Alembic Migration:**
  - Configured `alembic.ini` and `database/migrations/env.py`.
  - Created migration revision: `001_initial_schema.py`.
  - Executed migration: `alembic upgrade head`.
  - Verified in PostgreSQL: All 6 tables and indexes confirmed active.
* **Ingestion Foundation (`backend/app/services/ingestion_service.py`):**
  - Created `IngestionManager` with reference lookup caching and row validation.
  - Dry run on 1,000 crop records: 994 valid, 6 skipped (cleanly flagged missing production).

---

### 6. Verification Commands & Results

| Step | Command Executed | Result | Status |
| :--- | :--- | :--- | :--- |
| **PostgreSQL Connection** | `python scripts/test_db_connection.py` | Connected to PostgreSQL 17.12 as `krishiinsights_user` on `krishiinsights_db` | **PASSED** |
| **Dataset Profiling** | `python scripts/profile_datasets.py` | Generated JSON profiles and markdown summaries in `datasets/metadata/` | **PASSED** |
| **Alembic Migration** | `alembic upgrade head` | Applied `001_initial_schema` with transactional DDL | **PASSED** |
| **Table Inspection** | `python -c "inspect(engine)..."` | 6 tables verified in PostgreSQL (`states`, `districts`, `crops`, `agricultural_records`, `rainfall_records`, `prediction_records`) | **PASSED** |
| **Ingestion Dry Run** | `python -c "mgr.dry_run_crop_file(...)"` | Tested 1,000 records: 994 valid, 6 skipped | **PASSED** |
| **Backend Health Test** | `python backend/tests/test_health.py` | Health test passed; routes verified | **PASSED** |
| **Frontend Production Build** | `cd frontend && npx next build` | Compiled and verified with 0 errors | **PASSED** |

---

## Session 3: Stage 3 — Data Cleaning, Preprocessing & Full PostgreSQL Ingestion (November 17, 2026)

### 1. Objectives & Scope
Execute Stage 3 strictly per `AGENTS.md` and the Stage 3 Specification:
- Audit and normalize agricultural and meteorological datasets.
- Reorganize canonical datasets structure matching project specifications (`datasets/raw/` containing `crop_production.csv` and `rainfall.csv`).
- Populate lookup tables (`states`, `districts`, `crops`) idempotently with standard agricultural classifications.
- Ingest full 242,296 cleaned agricultural observations and 3,772 rainfall observations into PostgreSQL 17 (`krishiinsights_db`).
- Verify referential integrity, zero orphan records, and strict yield unit isolation (Coconut in `Nuts/Hectare` vs field crops in `Tonnes/Hectare`).
- Provide automated regression tests, verification CLI, and comprehensive ingestion documentation.

---

### 2. Files Created & Modified
* **Created:**
  - `scripts/run_ingestion.py`: Multi-command ingestion CLI supporting `--test`, `--full`, and `--verify`.
  - `backend/tests/test_stage3_ingestion.py`: Automated test suite covering crop classifications, yield math, unit isolation, and live database invariants.
  - `docs/DATA_INGESTION_REPORT.md`: Detailed engineering report on data provenance, validation steps, SQL verification outputs, and pgAdmin 4 queries.
* **Modified:**
  - `datasets/raw/`: Reorganized so `crop_production.csv` and `rainfall.csv` reside directly under `datasets/raw/`.
  - `backend/app/services/ingestion_service.py`: Implemented `IngestionPipeline` with chunked batch processing, in-memory reference caches, and atomic transaction commits.
  - `scripts/preprocess_data.py`: Updated raw input paths to reference canonical `datasets/raw/`.
  - `scripts/profile_datasets.py`: Updated raw dataset paths.
  - `datasets/README.md`: Updated directory structure and specifications.
  - `database/README.md`: Documented Stage 3 table row counts and verification queries.
  - `docs/ARCHITECTURE.md`: Updated data flow diagram to reflect finalized database state.
  - `CHANGELOG.md`: Recorded Stage 3 release notes.

---

### 3. Implementation Details & Technical Rationales

1. **District Multi-State Collision Resolution:**
   - There are 646 distinct district names in India, but 652 state-district pairs (e.g., *Aurangabad* in Bihar and Maharashtra; *Bilaspur* in Himachal Pradesh and Chhattisgarh).
   - *Rationale:* The database schema uses a composite constraint `uq_state_district (state_id, district_name)`. The ingestion service loads an in-memory tuple cache `(state_id, district_name_lower)` guaranteeing zero collisions and 100% accurate foreign key resolution.

2. **Strict Yield Formula & Integrity:**
   - In compliance with Rule 4.5 of `AGENTS.md`, Yield is strictly computed as:
     $$\text{Yield} = \frac{\text{Production}}{\text{Cultivated Area}}$$
   - Non-positive area ($\text{Area} \le 0$) and null production records were strictly filtered out during preprocessing.
   - The database verification confirms 0 null yields, 0 negative areas, and 0 negative productions.

3. **Measurement Unit Transparency:**
   - Coconut is reported by the Ministry of Agriculture in **Number of Nuts**, with a median production of ~239,000 nuts, resulting in yields of thousands of nuts/ha.
   - Field crops are reported in **Metric Tonnes**, resulting in yields typically ranging from 0.2 to 10 tonnes/ha.
   - *Rationale:* Every database record stores `production_unit` and `yield_unit` explicitly. Coconut is recorded with `Nuts/Hectare` (1,958 records) and all other crops with `Tonnes/Hectare` (240,338 records). They are isolated to prevent invalid numerical averaging.

4. **Batch Ingestion & Idempotency:**
   - Ingestion runs in 5,000-row chunks using PostgreSQL `ON CONFLICT DO NOTHING`.
   - Completed all 242,296 agricultural records in 251.3 seconds (~964 records/sec) with zero errors.
   - Re-running the pipeline results in 0 duplicate records inserted.

---

### 4. Verification Commands & Measured Results

| Step | Command Executed | Result | Status |
| :--- | :--- | :--- | :--- |
| **Test Ingestion & Idempotency** | `python scripts/run_ingestion.py --test` | 1,000 rows ingested; re-run inserted 0 duplicates | **PASSED** |
| **Full Ingestion** | `python scripts/run_ingestion.py --full` | 242,296 agricultural records + 3,772 rainfall records ingested in 251.3s | **PASSED** |
| **SQL Verification Audit** | `python scripts/run_ingestion.py --verify` | 33 states, 652 districts, 124 crops, 0 null yields, 0 orphans across all FKs | **PASSED** |
| **Stage 3 Unit & DB Tests** | `python backend/tests/test_stage3_ingestion.py` | 4 test suites passed (categories, yield math, unit distinction, DB invariants) | **PASSED** |
| **Full Backend Pytest** | `pytest backend/tests` | 6 passed in 2.53s | **PASSED** |
| **Backend Health Check** | `python backend/tests/test_health.py` | `status: healthy`, `database: connected` | **PASSED** |
| **Frontend Production Build** | `cd frontend && npx next build` | Next.js 16 (App Router) compiled with 0 errors | **PASSED** |

---

### 5. Next Steps
* Await user approval for Stage 3 completion.
* Stage 4 will focus on **Exploratory Data Analysis (EDA) & Statistical Analysis** (Jupyter notebooks, distribution curves, correlation analysis, and regional trends).

---

## Infrastructure Note: Neon Cloud PostgreSQL Project Linking & Agent Tooling (November 17, 2026)

### 1. Scope & Execution
* Linked the KrishiInsights repository to an existing Neon Serverless PostgreSQL project (`morning-glitter-97393312`) under organization `org-steep-leaf-69533238`.
* Configured Neon CLI 9.6.0 with user-level and project-level agent skills for Antigravity (`neon`, `neon-ai-gateway`, `neon-auth`, `neon-functions`, `neon-object-storage`, `neon-postgres`, `neon-realtime`).
* Configured hosted Neon MCP Server at `C:\Users\aayus\.gemini\config\mcp_config.json`.
* Populated branch environment variables into `.env.local` (excluded from git via `.gitignore`).
* Maintained local PostgreSQL development configuration in `backend/.env` untouched.
* Enhanced `backend/app/core/config.py` with dynamic SQLAlchemy dialect normalization (`postgresql://` -> `postgresql+psycopg2://`) and seamless `USE_NEON=true` environment toggling.
* Verified that zero database migrations, schema mutations, or table truncations were run on either database.
