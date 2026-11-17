# Machine Learning Data Directory

In accordance with KrishiInsights Stage 2 architecture:
- The single canonical source of truth for all datasets is the root-level `datasets/` directory:
  - Raw Agricultural Records: `datasets/raw/agriculture/crop_production.csv`
  - Raw Meteorological Records: `datasets/raw/rainfall/rainfall.csv`
  - Cleaned & Processed Records: `datasets/processed/clean_crop_data.csv`, `datasets/processed/combined_data.csv`
  - Dataset Profiles & Lineage: `datasets/metadata/`
- The ML module references datasets from `datasets/` via relative paths (`../../datasets/` or project root configuration).
- Duplicate physical data files are deliberately not maintained in `ml/data/` to eliminate repository bloat and prevent data drift.
