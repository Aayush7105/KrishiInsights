# Changelog — KrishiInsights

All notable changes to the KrishiInsights project will be documented in this file.

---

## [Stage 4: Independent Verification & Quality Audit] — 2026-11-18

### Audited & Verified
- **Verification Verdict:** Formally certified Stage 4 as **PASS** after completing independent verification across database invariants, statistical calculations, notebook execution, and documentation fidelity.
- **Audit Deliverable:** Published `docs/STAGE_4_VERIFICATION_REPORT.md` documenting comprehensive verification scorecard, methodology comparisons, and remediation log.

### Fixed & Remediated
- **Schema Reconciliation (`ml/src/database/connection.py`, `ml/src/analytics/rainfall_analysis.py`):** Fixed `rainfall_records` queries to use `source_id` instead of non-existent `source_subdivision`.
- **API Interface Consistency (`ml/src/analytics/crop_analysis.py`):** Added `limit: int = 10` parameter and dual return dictionary keys (`growth`/`fastest_growing`, `decline`/`declining`) to `get_crop_growth_and_decline_rankings`.
- **Diversity Metrics Enhancement (`ml/src/analytics/regional_analysis.py`):** Added `effective_crops_count` ($e^{H'}$) and `primary_crop` determination to `calculate_state_crop_diversity`.
- **Dictionary Key Hardening (`ml/src/analytics/rainfall_analysis.py`):** Updated `get_rainfall_summary_statistics` to return both structured nested and flat keys.
- **Dynamic Column Aliasing (`ml/src/analytics/outlier_analysis.py`):** Enabled dynamic column lookup supporting `yield` / `yield_amount`, `year` / `crop_year`, and `season` / `season_name`.
- **Documentation Numerical Alignment:** Reconciled statistics in `docs/AGRICULTURAL_ANALYSIS.md`, `docs/RAINFALL_ANALYSIS.md`, `docs/RAINFALL_AGRICULTURE_RELATIONSHIP.md`, `docs/STATISTICAL_FINDINGS.md`, and `docs/EDA_REPORT.md` to 100% match live Neon database totals for all field crops.
- **Notebook & Chart Verification:** Re-executed all 5 notebooks cell-by-cell with 0 errors via `scripts/test_execute_notebooks.py` and re-verified all 15 figures at 300 DPI.

---

## [Stage 4: Exploratory Data Analysis (EDA) & Statistical Analysis] — 2026-11-17

### Added
- **Core Analytical Engines (`ml/src/analytics/`):**
  - `agricultural_eda.py`: Overall descriptive statistics (mean, median, std, IQR, min, max) with strict unit isolation (Tonnes/Ha vs Nuts/Ha), annual aggregate trends (1997–2015), YoY percentage changes, long-term indices, and seasonal distributions.
  - `crop_analysis.py`: Single-crop profiles, top 10 rankings by production, area, and yield, production variability ($CV\%$), and 3-year smoothed growth/decline rankings.
  - `regional_analysis.py`: State-level performance leaderboards across 33 states/UTs, multi-state comparative queries, composite district rankings `(state_name, district_name)`, and Shannon Crop Diversity Index calculations.
  - `rainfall_analysis.py`: 115-year IMD meteorological analysis (1901–2015), Long Period Average (LPA = 1,180.72 mm), deficit/excess year classification, seasonal breakdown, and wettest/driest state rankings.
  - `correlation_analysis.py`: Paired seasonal correlations (Pearson $r$ and Spearman $\rho$), crop-specific rainfall sensitivities, and state-level sensitivity divergence.
  - `outlier_analysis.py`: Tukey's IQR and Z-score outlier detection, distinguishing clerical data artifacts from authentic agro-climatic extremes.
- **Database Access Layer (`ml/src/database/`):**
  - `connection.py`: Singleton SQLAlchemy connection manager with pooled/unpooled URL resolution, dynamic dialect normalization (`postgresql+psycopg2://`), and optimized query runners.
- **Publication-Grade Visualizations (`ml/reports/figures/` & `ml/src/visualization/`):**
  - Built 3 visualization modules: `agricultural_charts.py`, `rainfall_charts.py`, `comparison_charts.py`.
  - Created automated rendering pipeline: `ml/src/visualization/generate_all_figures.py`.
  - Generated 15 high-resolution 300 DPI PNG figures:
    - `agri_trends_production_area.png`, `agri_national_yield_trend.png`, `agri_seasonal_distribution.png`, `agri_top_crops_production.png`, `agri_top_crops_area.png`, `agri_top_crops_yield.png`, `agri_yield_distributions.png`, `rainfall_115yr_trend.png`, `rainfall_lpa_deviations.png`, `rainfall_seasonal_breakdown.png`, `rainfall_wettest_driest_states.png`, `correlation_rice_monsoon_scatter.png`, `correlation_paired_heatmap.png`, `correlation_state_sensitivity_contrast.png`, `outliers_crop_yield_boxplots.png`.
- **Programmatic Jupyter Notebooks (`ml/notebooks/`):**
  - Built and executed 5 self-contained, reproducible notebooks populated with verified stdout streams and execution counts:
    - `01_agricultural_eda.ipynb`
    - `02_crop_analysis.ipynb`
    - `03_regional_analysis.ipynb`
    - `04_rainfall_analysis.ipynb`
    - `05_rainfall_agriculture_relationship.ipynb`
- **Comprehensive Analytical Documentation Reports (`docs/`):**
  - Published 6 in-depth analytical reports with exact mathematical calculations and agronomic interpretations:
    - `docs/EDA_REPORT.md`
    - `docs/AGRICULTURAL_ANALYSIS.md`
    - `docs/REGIONAL_ANALYSIS.md`
    - `docs/RAINFALL_ANALYSIS.md`
    - `docs/RAINFALL_AGRICULTURE_RELATIONSHIP.md`
    - `docs/STATISTICAL_FINDINGS.md`
- **Automated Test Suite (`ml/tests/test_analytics.py`):**
  - Implemented 11 unit and integration test cases covering aggregate yield math, unit isolation, outlier detection formulas, Shannon diversity, and live Neon database queries.
  - 100% test pass rate achieved across all analytics and backend test suites (17 total tests).

---

## [Database Migration: Local PostgreSQL to Neon Serverless Postgres] — 2026-11-17

### Added
- **Full Database Migration to Neon Serverless Postgres (`neondb`):**
  - Generated timestamped PostgreSQL custom-format backup (`database/backups/krishiinsights_db_backup_20261117_224157.dump`, 3.30 MB).
  - Executed `pg_restore` into Neon project `morning-glitter-97393312` (`my-first-project`), organization `org-steep-leaf-69533238`, active branch `production`.
  - Transferred and verified all 33 states, 652 districts, 124 crops, 242,296 agricultural observations, 3,772 rainfall observations, 31 indexes and constraints, and Alembic version `001_initial_schema`.
  - 100% exact parity achieved across all statistical metrics, year ranges, yield units, and referential integrity (0 orphans).
- **Application Configuration Switch:**
  - Configured Neon as the primary, authoritative database across `.env` and `backend/.env`.
  - Configured pooled connection (`DATABASE_URL`) for FastAPI and SQLAlchemy runtime operations.
  - Configured direct unpooled connection (`DATABASE_URL_DIRECT`) for Alembic migrations and administrative DDL.
  - Hardened `backend/app/core/config.py` with dynamic SQLAlchemy dialect normalization and fail-fast validation (no silent local fallbacks).
- **Comprehensive Forensic Verification & Audit:**
  - Automated side-by-side audit runner created in `scripts/verify_neon_migration.py`.
  - Created `docs/NEON_MIGRATION_REPORT.md` documenting forensic proof of zero data loss and exact parity.
  - Verified application read and write-back functionality via `scripts/test_neon_primary_app.py`.
- **Team Collaboration & Architecture Standards:**
  - Prepared repository for five-member team collaboration with centralized shared database architecture.
  - Updated `.env.example` with clear, safe placeholders and team setup instructions.

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
