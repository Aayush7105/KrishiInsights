# Machine Learning & Analytics Module (`ml/`)

This directory houses the exploratory data analysis (EDA), statistical modeling, feature engineering pipelines, model training workflows, and evaluation artifacts for **KrishiInsights**.

---

## 1. Directory Structure

```text
ml/
├── data/
│   ├── raw/                 # Immutable official source datasets (crop_production.csv, rainfall.csv)
│   ├── interim/             # Intermediate transformations and merged partitions
│   └── processed/           # Validated, feature-ready datasets (clean_crop_data.csv, combined_data.csv)
├── notebooks/               # Jupyter exploration and experimental notebooks (01_eda, 02_training, etc.)
├── src/
│   ├── data/                # Data loading, validation, and ingestion scripts
│   ├── features/            # Feature transformation, categorical encoders, and scaling
│   ├── models/              # Estimator definitions, train/evaluation pipelines, and predictors
│   └── visualization/       # EDA plotting, correlation matrices, and distribution scripts
├── artifacts/               # Serialized model pipelines (.joblib) and training metadata
├── reports/                 # Generated diagnostic figures, evaluation reports, and metric logs
├── requirements.txt         # Data science and ML specific dependencies
└── README.md
```

---

## 2. Environment Management Strategy

In accordance with Section 5 of the KrishiInsights Architecture Guidelines:
1. **Separation of Concerns:** The ML analytics environment is isolated from the production backend API. The API service only requires runtime dependencies (`fastapi`, `uvicorn`, `joblib`, and `scikit-learn` for inference), keeping the production backend lightweight without development-heavy visualization tools like Jupyter or Seaborn.
2. **Reproducibility:** A dedicated virtual environment can be created for ML experiments:
   ```bash
   python -m venv ml/.venv
   # Windows:
   ml\.venv\Scripts\activate
   # Linux/macOS:
   source ml/.venv/bin/activate
   pip install -r ml/requirements.txt
   ```
3. **Artifact Promotion:** Models trained and validated in `ml/` (e.g. `random_forest_pipeline.joblib`) are versioned into `ml/artifacts/` alongside performance evaluation metrics (MAE, RMSE, $R^2$) before being loaded by the backend prediction service.
