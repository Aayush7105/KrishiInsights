# Changelog — KrishiInsights

All notable changes to the KrishiInsights project will be documented in this file.

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
