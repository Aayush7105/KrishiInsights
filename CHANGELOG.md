# Changelog — KrishiInsights

All notable changes to the KrishiInsights project will be documented in this file.

---

## [Stage 3: Data Cleaning, Preprocessing & PostgreSQL Ingestion] — 2026-11-17

### Added
- **Streamlined Datasets Structure:**
  - Reorganized canonical datasets structure to locate `crop_production.csv` and `rainfall.csv` directly under `datasets/raw/`.
  - Maintained cleaned records in `datasets/processed/clean_crop_data.csv` (242,296 records) and `combined_data.csv`.
- **Full Ingestion Pipeline (`backend/app/services/ingestion_service.py`):**
  - Implemented `IngestionPipeline` with chunked batch processing (5,000 records per batch) and in-memory lookup caching.
  - Standardized all 124 crops into 10 ICAR/DES taxonomic categories.
  - Handled district spatial collisions across states via composite unique key `(state_id, district_name)`.
  - Implemented PostgreSQL `ON CONFLICT DO NOTHING` for idempotent operations.
- **Ingestion Runner CLI (`scripts/run_ingestion.py`):**
  - Added CLI runner with `--test`, `--full`, and `--verify` commands.
- **Full PostgreSQL Ingestion Execution:**
  - Successfully ingested **33 states**, **652 districts**, **124 crops**, **3,772 rainfall records**, and **242,296 agricultural records** into PostgreSQL 17 (`krishiinsights_db`) in 251.3s.
  - Zero duplicate rows created on re-run (idempotency verified).
- **Yield Unit Integrity & Isolation:**
  - Standardized Coconut yield to `Nuts/Hectare` (1,958 records) and production to `Number of Nuts`.
  - Standardized field and horticultural crops to `Tonnes/Hectare` (240,338 records) and production to `Tonnes`.
  - 0 null yield records, 0 negative/zero area records, 0 negative production records.
- **Automated Regression Test Suite (`backend/tests/test_stage3_ingestion.py`):**
  - Unit tests for crop classification, yield derivation math, and coconut unit isolation.
  - Integration tests verifying PostgreSQL record counts, foreign key integrity (0 orphans), and invariant checks.
  - All 6 backend tests passing under pytest.
- **Documentation & Verification Reports:**
  - Published comprehensive `docs/DATA_INGESTION_REPORT.md` with complete provenance, table metrics, and verification queries.
  - Updated `datasets/README.md`, `database/README.md`, `docs/ARCHITECTURE.md`, and `docs/DEVELOPMENT_LOG.md`.

---

## [Stage 2: Dataset Research, Acquisition, and Database Design] — 2026-11-17

### Added
- **Dataset Reorganization & Canonical Storage:**
  - Established canonical root `datasets/` hierarchy (`raw/agriculture/`, `raw/rainfall/`, `interim/`, `processed/`, `metadata/`).
  - Audited and verified SHA-256 checksums across datasets.
  - Eliminated 71 MB of duplicate physical files from `ml/data/`, redirecting ML data access to the canonical `datasets/` root.
- **Dataset Profiling & Metadata Generation:**
  - Implemented automated profiling script in `scripts/profile_datasets.py`.
  - Generated structural and data quality profiles: `datasets/metadata/crop_production_profile.json`, `rainfall_profile.json`, and `DATASET_PROFILING_REPORT.md`.
  - Documented dataset provenance, URLs, licensing, and lineage in `datasets/metadata/dataset_sources.json`.
- **Database Architecture & PostgreSQL Implementation:**
  - Configured PostgreSQL 17 connection with environment-driven settings (`DATABASE_URL`) in `backend/app/core/config.py` and `backend/.env`.
  - Defined SQLAlchemy 2.x declarative models in `backend/app/models/agriculture.py`:
    - `State`, `District`, `Crop`, `AgriculturalRecord`, `RainfallRecord`, `PredictionRecord`.
  - Enforced relational integrity with cascading deletes, foreign keys, and composite uniqueness constraints (`uq_state_district`, `uq_agri_record`, `uq_state_year_rainfall`).
- **Alembic Database Migration Pipeline:**
  - Initialized Alembic configuration in `alembic.ini` and `database/migrations/env.py`.
  - Created initial migration revision `001_initial_schema.py`.
  - Successfully applied migration to `krishiinsights_db` via `alembic upgrade head`.
  - Verified active creation of all 6 application tables and indexes in PostgreSQL 17.
- **Ingestion Foundation Service:**
  - Created modular ingestion service in `backend/app/services/ingestion_service.py` featuring lookup caches, record validation, and dry-run execution.
  - Verified dry-run execution on raw crop dataset sample.
- **Connection Verification Script:**
  - Created `scripts/test_db_connection.py` for safe database testing with password masking.

---

## [Stage 1: Project Initialization and Environment Setup] — 2026-11-17

### Added
- **Permanent Architecture Guidelines:** Created root `AGENTS.md` detailing project identity, technology stack, mandatory data integrity rules, ML evaluation standards, development protocols, and 12-stage implementation plan.
- **Project Monorepo Structure:** Initialized standardized modular directory architecture (`frontend/`, `backend/`, `ml/`, `database/`, `docs/`, `scripts/`).
- **Next.js Frontend Foundation:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, production build verified.
- **FastAPI Modular Backend:** Entrypoint, CORS middleware, `GET /api/health` endpoint, automated test suite.
- **Environment & Git Setup:** `.env.example`, `.gitignore` with secret exclusions.
