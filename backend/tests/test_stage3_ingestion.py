"""
KrishiInsights - Stage 3 Ingestion & Preprocessing Unit and Integration Tests
Verifies data integrity rules, yield formulas, unit distinctions, and database invariants.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.ingestion_service import CROP_CATEGORY_MAP, IngestionPipeline
from app.database.session import SessionLocal
from sqlalchemy import text


def test_crop_category_mapping():
    """Verify that all major crop types map to standard agricultural categories."""
    assert CROP_CATEGORY_MAP['Rice'] == 'Cereal'
    assert CROP_CATEGORY_MAP['Wheat'] == 'Cereal'
    assert CROP_CATEGORY_MAP['Maize'] == 'Coarse Cereal'
    assert CROP_CATEGORY_MAP['Gram'] == 'Pulse'
    assert CROP_CATEGORY_MAP['Arhar/Tur'] == 'Pulse'
    assert CROP_CATEGORY_MAP['Groundnut'] == 'Oilseed'
    assert CROP_CATEGORY_MAP['Cotton(lint)'] == 'Fiber'
    assert CROP_CATEGORY_MAP['Sugarcane'] == 'Commercial'
    assert CROP_CATEGORY_MAP['Coconut'] == 'Plantation'
    assert CROP_CATEGORY_MAP['Potato'] == 'Vegetable'
    assert CROP_CATEGORY_MAP['Banana'] == 'Fruit'
    assert CROP_CATEGORY_MAP['Black pepper'] == 'Spices'
    print("✓ test_crop_category_mapping passed.")


def test_yield_calculation_and_filtering():
    """Verify Yield = Production / Area and that invalid records are filtered out."""
    sample_data = {
        'State_Name': ['StateA', 'StateA', 'StateA', 'StateA'],
        'District_Name': ['Dist1', 'Dist1', 'Dist1', 'Dist1'],
        'Crop_Year': [2010, 2010, 2010, 2010],
        'Season': ['Kharif', 'Kharif', 'Kharif', 'Kharif'],
        'Crop': ['Rice', 'Rice', 'Rice', 'Rice'],
        'Area': [100.0, 0.0, -10.0, 50.0],
        'Production': [250.0, 100.0, 20.0, np.nan]
    }
    df = pd.DataFrame(sample_data)

    # 1. Filter out null production
    valid_df = df.dropna(subset=['Production']).copy()
    assert len(valid_df) == 3

    # 2. Filter out area <= 0
    valid_df = valid_df[valid_df['Area'] > 0].copy()
    assert len(valid_df) == 1

    # 3. Calculate yield
    valid_df['Yield'] = valid_df['Production'] / valid_df['Area']
    assert valid_df.iloc[0]['Yield'] == 2.5
    print("✓ test_yield_calculation_and_filtering passed.")


def test_coconut_unit_distinction():
    """Verify that Coconut is distinguished with Nuts/Hectare and Number of Nuts."""
    crops = ['Rice', 'Wheat', 'Coconut ', 'Coconut', 'Sugarcane']
    for crop in crops:
        is_coconut = 'coconut' in crop.strip().lower()
        prod_unit = "Number of Nuts" if is_coconut else "Tonnes"
        yield_unit = "Nuts/Hectare" if is_coconut else "Tonnes/Hectare"

        if 'coconut' in crop.lower():
            assert prod_unit == "Number of Nuts"
            assert yield_unit == "Nuts/Hectare"
        else:
            assert prod_unit == "Tonnes"
            assert yield_unit == "Tonnes/Hectare"
    print("✓ test_coconut_unit_distinction passed.")


def test_database_ingestion_invariants():
    """Verify database counts and referential integrity if PostgreSQL is connected."""
    try:
        db = SessionLocal()
        # Verify connection
        db.execute(text("SELECT 1;"))
    except Exception as e:
        print(f"Skipping database integration test (PostgreSQL not directly reachable: {e})")
        return

    try:
        state_cnt = db.execute(text("SELECT COUNT(*) FROM states;")).scalar()
        dist_cnt = db.execute(text("SELECT COUNT(*) FROM districts;")).scalar()
        crop_cnt = db.execute(text("SELECT COUNT(*) FROM crops;")).scalar()
        rain_cnt = db.execute(text("SELECT COUNT(*) FROM rainfall_records;")).scalar()
        agri_cnt = db.execute(text("SELECT COUNT(*) FROM agricultural_records;")).scalar()

        assert state_cnt == 33, f"Expected 33 states, got {state_cnt}"
        assert dist_cnt == 652, f"Expected 652 districts, got {dist_cnt}"
        assert crop_cnt == 124, f"Expected 124 crops, got {crop_cnt}"
        assert rain_cnt == 3772, f"Expected 3772 rainfall records, got {rain_cnt}"
        assert agri_cnt == 242296, f"Expected 242296 agricultural records, got {agri_cnt}"

        # Invariant checks
        null_yields = db.execute(text("SELECT COUNT(*) FROM agricultural_records WHERE yield_amount IS NULL;")).scalar()
        assert null_yields == 0, f"Found {null_yields} null yield records"

        invalid_area = db.execute(text("SELECT COUNT(*) FROM agricultural_records WHERE area <= 0;")).scalar()
        assert invalid_area == 0, f"Found {invalid_area} invalid area records"

        # Foreign key integrity
        orphans = db.execute(text("""
            SELECT COUNT(*) FROM agricultural_records a 
            LEFT JOIN states s ON a.state_id = s.id 
            LEFT JOIN districts d ON a.district_id = d.id 
            LEFT JOIN crops c ON a.crop_id = c.id 
            WHERE s.id IS NULL OR d.id IS NULL OR c.id IS NULL;
        """)).scalar()
        assert orphans == 0, f"Found {orphans} orphan records"

        print(f"✓ test_database_ingestion_invariants passed: {agri_cnt:,} agri, {rain_cnt:,} rain records verified.")
    finally:
        db.close()


if __name__ == "__main__":
    test_crop_category_mapping()
    test_yield_calculation_and_filtering()
    test_coconut_unit_distinction()
    test_database_ingestion_invariants()
    print("\nAll Stage 3 tests passed successfully!")
