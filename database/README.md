# Database Architecture & Management (`database/`)

This directory documents the relational schema, migration management, and connection configuration for **KrishiInsights**.

---

## 1. Database Technology Stack

* **Database Engine:** PostgreSQL 17 (Local development port: 5432, database: `krishiinsights_db`, user: `krishiinsights_user`).
* **Object-Relational Mapping (ORM):** SQLAlchemy 2.x
* **Migration Management:** Alembic 1.20+
* **Driver:** `psycopg2-binary` (PostgreSQL standard binary driver)
* **Design Philosophy:** Environment-based configuration allowing zero-downtime switching between local PostgreSQL and hosted cloud instances (e.g. Supabase, AWS RDS, Neon) without application code changes.

---

## 2. Relational Schema & Entity-Relationship Design

The schema is implemented in `backend/app/models/agriculture.py` and reflected in migration `001_initial_schema`:

```text
┌─────────────────┐       ┌─────────────────┐
│     states      │       │      crops      │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──┐   │ id (PK)         │◄──┐
│ state_name      │   │   │ crop_name       │   │
│ source_code     │   │   │ crop_category   │   │
└────────┬────────┘   │   └────────┬────────┘   │
         │ 1          │            │ 1          │
         │            │            │            │
         ▼ N          │            │            │
┌─────────────────┐   │            │            │
│    districts    │   │            │            │
├─────────────────┤   │            │            │
│ id (PK)         │   │            │            │
│ state_id (FK)   │   │            │            │
│ district_name   │   │            │            │
│ source_code     │   │            │            │
└────────┬────────┘   │            │            │
         │ 1          │            │            │
         │            │            │            │
         ▼ N          │ N          ▼ N          │ N
┌─────────────────────┴────────────┴────────────┴───┐
│               agricultural_records                │
├───────────────────────────────────────────────────┤
│ id (PK)                                           │
│ state_id (FK -> states.id)                        │
│ district_id (FK -> districts.id)                  │
│ crop_id (FK -> crops.id)                          │
│ season                                            │
│ year                                              │
│ area (Hectares)                                   │
│ production (Tonnes / Nuts)                        │
│ yield_amount (Tonnes/Ha or Nuts/Ha)               │
│ area_unit, production_unit, yield_unit            │
└───────────────────────────────────────────────────┘

┌─────────────────┐       ┌───────────────────────┐
│ rainfall_records│       │  prediction_records   │
├─────────────────┤       ├───────────────────────┤
│ id (PK)         │       │ id (PK)               │
│ state_id (FK)   │       │ input_features (JSON) │
│ year            │       │ predicted_yield       │
│ annual_rainfall │       │ unit                  │
│ monsoon_rainfall│       │ model_name            │
│ rabi_rainfall   │       │ model_version         │
│ source_id (IMD) │       │ created_at            │
└─────────────────┘       └───────────────────────┘
```

---

## 3. Key Constraints & Optimization

1. **Foreign Key Integrity:**
   * `districts.state_id` $\rightarrow$ `states.id` (with `ON DELETE CASCADE`).
   * `agricultural_records.state_id` $\rightarrow$ `states.id`.
   * `agricultural_records.district_id` $\rightarrow$ `districts.id`.
   * `agricultural_records.crop_id` $\rightarrow$ `crops.id`.
   * `rainfall_records.state_id` $\rightarrow$ `states.id`.
2. **Composite Uniqueness Constraints:**
   * `districts`: `(state_id, district_name)` ensures no duplicate district names within a state.
   * `agricultural_records`: `(state_id, district_id, crop_id, season, year)` prevents duplicate crop observation ingestion.
   * `rainfall_records`: `(state_id, year)` guarantees a single state-aggregated rainfall metric per year.
3. **B-Tree Indexing Strategy:**
   * High-cardinality search columns: `states.state_name`, `districts.district_name`, `crops.crop_name`.
   * Multi-dimensional filtering columns: `agricultural_records.year`, `agricultural_records.season`, `agricultural_records.yield_amount`.
   * Query foreign keys: `agricultural_records.state_id`, `agricultural_records.district_id`, `agricultural_records.crop_id`.

---

## 4. Migration & Management Instructions

Migrations are version-controlled via Alembic at the root of the project:

```bash
# Check current migration revision
alembic current

# Run migrations to latest schema (online)
alembic upgrade head

# Generate SQL DDL without applying (offline preview)
alembic upgrade head --sql

# Rollback one migration
alembic downgrade -1
```

---

## 5. Connection Configuration

The application reads `DATABASE_URL` dynamically from the environment. Credentials are never hardcoded.

```env
# Local Development (PostgreSQL 17 - Default)
DATABASE_URL=postgresql+psycopg2://krishiinsights_user:<password>@localhost:5432/krishiinsights_db

# Hosted Production (Neon Serverless Postgres)
# Toggle USE_NEON=true in .env to use Neon credentials from .env.local without changing code
USE_NEON=true
# DATABASE_URL=postgresql+psycopg2://<user>:<password>@<neon-endpoint>.neon.tech/<dbname>?sslmode=require
```

Connection verification can be tested at any time:
```bash
python scripts/test_db_connection.py
```

---

## 6. Stage 3 Ingested Data Metrics & Verification

All tables are populated and verified as of Stage 3:

| Table Name | Record Count | Integrity Status |
| :--- | :--- | :--- |
| `states` | 33 | 100% Unique |
| `districts` | 652 | Unique per `(state_id, district_name)` |
| `crops` | 124 | Categorized into 10 ICAR/DES groups |
| `rainfall_records` | 3,772 | 1901–2015 coverage, 0 orphans |
| `agricultural_records` | 242,296 | 1997–2015 coverage, 0 null yields, 0 orphans |
| `prediction_records` | 0 | Ready for Stage 10 inference logs |

Verification runner:
```bash
python scripts/run_ingestion.py --verify
```
