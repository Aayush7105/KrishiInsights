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
