# AGENTS.md — KrishiInsights Development & Architecture Guidelines

> **Project Title:** KrishiInsights — An Agricultural Data Analytics and Crop Yield Intelligence Platform Using Machine Learning  
> **Academic Context:** Final-Year B.Tech Computer Science Project  
> **Role:** Lead Software Architect & Development Agent

---

## 1. Project Overview & Objectives

**KrishiInsights** is a web-based agricultural data analytics platform focused on historical Indian agricultural and meteorological data.

### Primary Purpose
Help users explore, understand, compare, and analyze historical agricultural records through interactive dashboards, charts, multi-level filters, and statistical insights.

> [!IMPORTANT]
> **Data analytics is the primary focus of this project.** Machine learning is a supporting module for estimating crop yield under specified conditions, not the entire project.

### Core Objectives
1. **Historical Analytics:** Analyze historical crop production, cultivated area, and yield across India.
2. **Multi-dimensional Exploration:** Explore agricultural data filtered by state, district, crop, season, and year.
3. **Comparative Analysis:** Compare performance across crops, seasons, and geographic regions.
4. **Rainfall & Climate Analysis:** Examine historical rainfall patterns and their statistical relationships with crop yield.
5. **Statistical Insights:** Present descriptive statistics, distribution curves, and trend lines through interactive visualizations.
6. **Machine Learning Intelligence:** Provide regression-based crop yield estimation with documented accuracy metrics and caveats.
7. **Report Generation:** Export downloadable analytical summaries and reports.

---

## 2. Technology Stack

Follow this stack strictly unless a modification is technically mandatory and explicitly approved:

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js (App Router), React, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| **Backend API** | Python, FastAPI, SQLAlchemy, Pydantic |
| **Database** | PostgreSQL |
| **Data Analytics & ML** | Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, Joblib, Jupyter Notebook |
| **Other Tools** | Git & GitHub, Postman, ReportLab (PDF export) |

---

## 3. Main Application Modules

The application consists of eight functional modules to be implemented incrementally:

1. **Dashboard:** High-level agricultural overview, production totals, cultivated area, average yield, trends, and summary KPIs.
2. **Data Explorer:** Searchable, sortable, and paginated table of records with dependent state/district/crop filters.
3. **Crop Analysis:** Single-crop performance analysis and multi-crop comparison over common time windows.
4. **Regional Comparison:** State-wise and district-wise comparisons of production and yield.
5. **Rainfall Analysis:** Seasonal and annual rainfall trends and correlation analysis with crop yield.
6. **Yield Prediction:** Form-driven yield estimation using trained regression pipelines.
7. **Model Performance:** Comparative evaluation metrics (MAE, RMSE, $R^2$) and actual vs. predicted diagnostics.
8. **Reports:** Downloadable summary reports (PDF / CSV) capturing selected analytics and filters.

---

## 4. Data Integrity Rules (Mandatory)

1. **Authentic Sources Only:** Source all data from credible official repositories:
   - [Open Government Data Platform (data.gov.in)](https://www.data.gov.in/)
   - [National Data & Analytics Platform (NDAP, NITI Aayog)](https://ndap.niti.gov.in/)
   - [India Meteorological Department (IMD mausam.imd.gov.in)](https://mausam.imd.gov.in/)
2. **No Data Fabrication:** Never fabricate agricultural statistics, invent sources, or falsify download citations.
3. **Raw Data Immutability:** Never overwrite or mutate raw datasets in `datasets/raw/`.
4. **Isolated Processing:** Always save cleaned, transformed, and joined data in `datasets/processed/`.
5. **Strict Yield Definition:**
   $$\text{Yield} = \frac{\text{Production}}{\text{Cultivated Area}}$$
   Compute yield only when production and cultivated area have valid values, positive area ($>0$), and documented units.
6. **Unit Transparency:** Always track and document measurement units:
   - Field crops: Production in **Tonnes**, Area in **Hectares**, Yield in **Tonnes/Hectare**.
   - Tree crops (e.g., Coconut): Production in **Number of Nuts**, Yield in **Nuts/Hectare**.
7. **Granular Alignment:** Do not merge datasets with incompatible spatial or temporal granularities without documented, validated aggregation (e.g., IMD subdivisions mapped to states).
8. **Sample Data Disclosure:** If synthetic or demonstration data is ever temporarily used for UI testing, explicitly label it as mock data.

---

## 5. Analytics & Machine Learning Rules

### Data Analytics
- Prioritize exploratory data analysis, descriptive statistics (mean, median, variance, quantiles), trends, and distributions.
- Dashboard figures must be computed from actual database/dataset records.
- Keep filters synced and consistent across dependent views.
- Clearly separate production (total volume) from yield (efficiency per hectare).
- **Correlation $\neq$ Causation:** Rainfall correlation must include explicit caveats regarding irrigation, fertilizer, soil, and management practices.

### Machine Learning
- **Candidate Models:** Linear Regression and Random Forest Regressor (Decision Tree as baseline comparison).
- **Evaluation Metrics:** Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Coefficient of Determination ($R^2$). Report MAE and RMSE in target units ($\text{Tonnes/Ha}$).
- **Validation Strategy:** Chronological holdout splitting (train on earlier years, evaluate on later held-out years).
- **Target Leakage Prevention:** Never use `Production` as an input feature to predict `Yield`, because Yield is derived from Production.
- **Inference Reality:** Features must only include attributes known at planting/prediction time.
- **Model Persistence:** Save trained estimators and their transformers together using `joblib`.
- **Honest Disclaimers:** Present predictions as historical statistical estimates, never as guaranteed future outcomes.

---

## 6. Software Development Rules

1. **Inspect Before Changing:** Always inspect existing files, configurations, and working code before editing.
2. **Preserve Working Code:** Do not break existing functionality or delete working files without justification.
3. **Architectural Separation:** Maintain strict boundaries between frontend UI, backend API, database layer, analytics scripts, and ML models.
4. **Component Reusability:** Build reusable UI components (KPI cards, chart containers, filter bars) and reusable backend services.
5. **Naming Conventions:** Use clear, self-documenting identifiers for variables, functions, endpoints, and components.
6. **Robust Validation:** Validate API requests and responses using Pydantic schemas; validate frontend form inputs before submission.
7. **No Fake Placeholders:** Do not introduce empty mock implementations and claim them as completed features.
8. **Stack Consistency:** Do not change or introduce secondary backend/frontend frameworks without explicit instruction.
9. **Verification First:** Test every modification (run scripts, check endpoints, or verify builds) before concluding a task.

---

## 7. Documentation Rules (Mandatory)

Maintain clear, accurate, and up-to-date documentation across four key files:

### `README.md`
Project overview, goals, technology stack, directory structure, prerequisites, setup instructions, backend/frontend run commands, API summary, and current completion status.

### `CHANGELOG.md`
Chronological log of changes grouped by date and stage:
- Date
- Stage / Module
- Features added
- Fixes applied
- Dependency or config changes

### `docs/DEVELOPMENT_LOG.md`
Detailed developer diary explaining:
- What was implemented in each session
- Files created or modified
- Technical decisions and rationales (written so student developers can learn)
- Commands run and verification test results
- Known limitations and immediate next steps

### `docs/ARCHITECTURE.md`
System design, module interactions, data flows, database entity-relationship schema, API contract patterns, and ML pipeline structure.

> [!NOTE]
> **Describe reality:** Document features only when they are genuinely implemented and tested, never when they are merely planned.

---

## 8. Project Development Stages

Development follows an incremental 12-stage plan. **Only implement a stage when explicitly instructed.**

1. **Stage 1:** Project initialization and environment setup.
2. **Stage 2:** Dataset research, acquisition, and database design.
3. **Stage 3:** Data cleaning, preprocessing, and database ingestion.
4. **Stage 4:** Exploratory data analysis (EDA) and statistical analysis.
5. **Stage 5:** FastAPI backend and analytics APIs.
6. **Stage 6:** Frontend architecture and core dashboard.
7. **Stage 7:** Data Explorer, Crop Analysis, and Regional Comparison modules.
8. **Stage 8:** Rainfall Analysis module.
9. **Stage 9:** Machine Learning model development, validation, and evaluation.
10. **Stage 10:** Prediction API and frontend integration.
11. **Stage 11:** Downloadable reports and optional geographical visualization.
12. **Stage 12:** End-to-end testing, performance optimization, deployment, and final documentation.

---

## 9. Operating Protocol for Future Tasks

When receiving a development task:
1. **Read `AGENTS.md`** first to align with rules and constraints.
2. **Inspect the workspace** to verify the current file tree and recent commits.
3. **Review documentation** (`README.md`, `DEVELOPMENT_LOG.md`) to establish context.
4. **Bound the scope** to the exact requested task.
5. **Execute changes** cleanly within that specific scope.
6. **Verify and test** the modifications.
7. **Update documentation** (`README.md`, `CHANGELOG.md`, `DEVELOPMENT_LOG.md`).
8. **Report summary:** State changed files, executed commands, test results, and next logical step without auto-advancing.
