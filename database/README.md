# Database Architecture & Management (`database/`)

This directory is reserved for database migration scripts, initial DDL schemas, and seed automation for **KrishiInsights**.

---

## 1. Planned Database Technology

* **Primary Database Engine:** PostgreSQL 15+
* **ORM & Database Toolkit:** SQLAlchemy 2.x
* **Migration Management:** Alembic
* **Connection Pooling:** SQLAlchemy `QueuePool` with asynchronous or synchronous connection handling via environment variables.

---

## 2. Directory Layout

```text
database/
├── migrations/            # Version-controlled schema migration scripts (managed via Alembic)
│   └── versions/          # Individual timestamped migration versions
└── README.md              # Database architectural strategy and connection guidelines
```

---

## 3. Configuration & Strategy

1. **Decoupled Credentials:** Database connection strings are never committed to version control. They are injected via `DATABASE_URL` in the environment configuration (`.env`).
2. **Schema Design (Stage 2/3):** The relational schema will be defined after dataset verification, implementing:
   * `states`: State identifiers and administrative names.
   * `districts`: District entities linked to states via foreign keys.
   * `crops`: Normalized crop entities and classification categories.
   * `agricultural_records`: Granular production, cultivated area, and computed yield records.
   * `rainfall_records`: IMD subdivision and state-level historical precipitation.
   * `prediction_records`: Historical audit log of user yield prediction queries.
3. **Indexes:** Optimized B-tree indexes will be established on frequently queried dimensions (`state_id`, `district_id`, `crop_id`, `year`, `season`).
