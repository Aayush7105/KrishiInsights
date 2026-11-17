# KrishiInsights — System Architecture

This document describes the high-level system architecture, component boundaries, and communication patterns of the **KrishiInsights** platform.

---

## 1. Monorepo Architectural Overview

KrishiInsights adopts a modular monorepo pattern that cleanly separates the user interface, backend application programming interface, machine learning training workflows, and database layers:

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
│     PostgreSQL Database     │ │   Trained Model Artifacts   │
│  (Relational Storage, DDL)  │ │   (.joblib, Scikit-learn)   │
└─────────────────────────────┘ └─────────────────────────────┘
                                              ▲
                                         Model Training
                                              │
                                ┌─────────────┴───────────────┐
                                │      Machine Learning       │
                                │   (Pandas, Scikit-learn)    │
                                └─────────────────────────────┘
```

---

## 2. Component Responsibilities

### 2.1 Frontend (`frontend/`)
* **Role:** Presentation and user interaction layer.
* **Responsibilities:**
  * Render responsive KPI metric cards, data tables, and interactive Recharts visualizations.
  * Provide dynamic, dependent filtering controls (e.g., selecting a state dynamically filters available districts).
  * Host the crop yield estimation form with input validation.
  * Consume JSON data from backend REST endpoints via standard `fetch` or `axios`.
  * Display explicit loading, error, and empty states.

### 2.2 Backend (`backend/`)
* **Role:** Business logic, query orchestration, and prediction inference service.
* **Responsibilities:**
  * Expose versioned REST endpoints (`/api/dashboard`, `/api/agriculture`, `/api/analytics`, `/api/predictions`).
  * Validate request inputs and response structures using Pydantic models.
  * Query the PostgreSQL database using SQLAlchemy.
  * Load pre-trained machine learning pipelines (`joblib`) into memory on startup and generate yield estimates without training during request handling.
  * Enforce Cross-Origin Resource Sharing (CORS) rules for frontend access.

### 2.3 Machine Learning Module (`ml/`)
* **Role:** Offline data science experimentation, exploratory analysis, and model training.
* **Responsibilities:**
  * Clean, preprocess, and merge raw agricultural and rainfall records.
  * Perform exploratory data analysis (EDA) and generate diagnostic charts.
  * Train regression pipelines (Linear Regression, Decision Tree, Random Forest).
  * Prevent target leakage (never predicting Yield using Production).
  * Validate models using chronological holdout splits and evaluate with MAE, RMSE, and $R^2$.
  * Serialize approved model pipelines to `ml/artifacts/` for backend deployment.

### 2.4 Database Layer (`database/`)
* **Role:** Structured relational data persistence.
* **Responsibilities:**
  * Store normalized entities (`states`, `districts`, `crops`, `agricultural_records`, `rainfall_records`, `prediction_records`).
  * Maintain referential integrity via foreign key constraints.
  * Provide indexed queries for fast multi-dimensional filtering across states, crops, and years.
  * Version schema modifications using Alembic migrations.

---

## 3. Communication Patterns

1. **Client-to-Server Communication:**
   * All frontend-to-backend communication occurs over HTTP/HTTPS using standard REST conventions.
   * Payloads and query parameters are serialized as JSON.
2. **Environment Isolation:**
   * In development:
     * Frontend: `http://localhost:3000`
     * Backend: `http://localhost:8000`
     * Base URL configured via `NEXT_PUBLIC_API_URL` in frontend environment.
3. **Decoupled Deployment Readiness:**
   * Because the frontend and backend communicate strictly via HTTP, they can be deployed together or independently (e.g., Next.js on Vercel and FastAPI on a containerized host like Render or Docker).
