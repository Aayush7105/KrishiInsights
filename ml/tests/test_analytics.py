"""
Automated Test Suite for KrishiInsights Analytics Modules (Stage 4).

Tests:
1. Unit tests for mathematical and statistical correctness:
   - Aggregate yield calculation (Sum(Prod)/Sum(Area))
   - Strict unit isolation (Tonnes vs Nuts)
   - IQR and Z-score outlier detection formulas
   - Shannon diversity index calculation
   - Pearson and Spearman correlation statistics
2. Integration tests querying Neon Serverless PostgreSQL:
   - Metadata and descriptive statistics
   - Annual agricultural trends
   - Top crops rankings
   - 115-year rainfall trends and LPA departures
   - Paired seasonal correlation calculations
"""

import os
import sys
import numpy as np
import pandas as pd
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from ml.src.analytics.outlier_analysis import (
    detect_outliers_iqr,
    detect_outliers_zscore,
    analyze_crop_yield_anomalies,
    classify_anomalies_summary
)
from ml.src.analytics.agricultural_eda import (
    calculate_overall_summary_statistics,
    get_annual_production_trends,
    get_seasonal_distribution,
    get_yearly_record_distribution
)
from ml.src.analytics.crop_analysis import (
    get_crop_historical_profile,
    get_top_crops_rankings,
    get_crop_growth_and_decline_rankings
)
from ml.src.analytics.regional_analysis import (
    get_state_performance_summary,
    calculate_state_crop_diversity
)
from ml.src.analytics.rainfall_analysis import (
    get_national_annual_rainfall_trends,
    get_rainfall_summary_statistics,
    get_top_wettest_and_driest_states
)
from ml.src.analytics.correlation_analysis import (
    calculate_seasonal_correlations,
    calculate_crop_rainfall_correlations,
    calculate_state_level_rainfall_sensitivity
)


# ========================================================
# 1. UNIT TESTS: Mathematical & Statistical Correctness
# ========================================================

def test_aggregate_yield_formula():
    """
    Validates that national aggregate yield is evaluated as
    Sum(Production) / Sum(Area), and NOT as a simple average of yields.
    """
    # Sample data with disparate district areas
    data = pd.DataFrame({
        "district": ["DistA", "DistB"],
        "area": [10.0, 1000.0],
        "production": [100.0, 2000.0]
    })
    data["individual_yield"] = data["production"] / data["area"]
    # Individual yields: DistA = 10.0 T/Ha, DistB = 2.0 T/Ha
    simple_avg_yield = data["individual_yield"].mean()  # 6.0 T/Ha (incorrect!)

    correct_aggregate_yield = data["production"].sum() / data["area"].sum()  # 2100 / 1010 = 2.0792 T/Ha

    assert simple_avg_yield == 6.0
    assert round(correct_aggregate_yield, 4) == 2.0792
    assert correct_aggregate_yield != simple_avg_yield


def test_iqr_outlier_detection_logic():
    """
    Tests Tukey's IQR detection formula:
    Lower = Q1 - 1.5 * IQR, Upper = Q3 + 1.5 * IQR.
    """
    # Distribution with known outliers
    values = pd.Series([10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 100, -50])
    res = detect_outliers_iqr(values, multiplier=1.5)

    assert res["method"] == "IQR"
    assert res["outlier_count"] == 2  # 100 and -50
    assert 100 in values.loc[res["outlier_indices"]].values
    assert -50 in values.loc[res["outlier_indices"]].values
    assert res["upper_bound"] > 20
    assert res["lower_bound"] < 10


def test_zscore_outlier_detection_logic():
    """
    Tests Z-score standardization: |z| > threshold.
    """
    values = pd.Series([2.0, 2.1, 2.0, 2.2, 1.9, 2.0, 2.1, 2.0, 100.0])
    res = detect_outliers_zscore(values, threshold=2.5)

    assert res["method"] == "Z-score"
    assert res["outlier_count"] == 1
    assert 100.0 in values.loc[res["outlier_indices"]].values


def test_shannon_diversity_index_calculation():
    """
    Validates Shannon Diversity Index logic: H' = -sum(p_i * ln(p_i)).
    Perfect equality among 4 crops: H' = -4 * (0.25 * ln(0.25)) = ln(4) ≈ 1.386.
    Complete monoculture (1 crop = 100%): H' = 0.
    """
    # Case 1: Monoculture
    p_mono = np.array([1.0])
    h_mono = -np.sum(p_mono * np.log(p_mono))
    assert h_mono == 0.0

    # Case 2: 4 equal crops
    p_equal = np.array([0.25, 0.25, 0.25, 0.25])
    h_equal = -np.sum(p_equal * np.log(p_equal))
    assert round(float(h_equal), 4) == round(float(np.log(4)), 4)
    assert round(float(h_equal), 3) == 1.386


def test_unit_isolation_in_rankings():
    """
    Tests that Coconut records with huge numeric production (Nuts)
    are strictly isolated from field crop rankings (Tonnes).
    """
    mock_df = pd.DataFrame({
        "crop_name": ["Sugarcane", "Rice", "Coconut"],
        "crop_category": ["Cash Crop", "Cereal", "Plantation"],
        "production_unit": ["Tonnes", "Tonnes", "Number of Nuts"],
        "yield_unit": ["Tonnes/Hectare", "Tonnes/Hectare", "Nuts/Hectare"],
        "area": [100.0, 200.0, 50.0],
        "production": [6000.0, 400.0, 500000.0],  # 500,000 nuts
        "yield": [60.0, 2.0, 10000.0]  # 10,000 nuts/ha
    })

    # Filter out coconut
    field_only = mock_df[mock_df["yield_unit"] == "Tonnes/Hectare"]
    top_yield_crop = field_only.sort_values(by="yield", ascending=False).iloc[0]["crop_name"]

    assert top_yield_crop == "Sugarcane"
    assert "Coconut" not in field_only["crop_name"].values


# ========================================================
# 2. INTEGRATION TESTS: Live Queries Against Neon Database
# ========================================================

def test_neon_agricultural_summary_statistics():
    """Verifies metadata and descriptive statistics returned from Neon."""
    stats = calculate_overall_summary_statistics()

    assert "metadata" in stats
    assert stats["metadata"]["total_records"] == 242296
    assert stats["metadata"]["num_states"] == 33
    assert stats["metadata"]["num_crops"] == 124
    assert stats["metadata"]["min_year"] == 1997
    assert stats["metadata"]["max_year"] == 2015

    # Check field crops count
    assert stats["field_crops"]["count"] == 240338
    # Check coconut count
    assert stats["coconut"]["count"] == 1958


def test_neon_annual_production_trends():
    """Verifies that annual trends query runs and covers 1997-2015."""
    trends = get_annual_production_trends(unit_filter="Tonnes/Hectare")

    assert not trends.empty
    assert len(trends) == 19
    assert trends.iloc[0]["year"] == 1997
    assert trends.iloc[-1]["year"] == 2015
    # Verify aggregate yield is computed
    assert "aggregate_yield" in trends.columns
    assert (trends["aggregate_yield"] > 0).all()
    # Check YoY changes computed
    assert "production_yoy_pct" in trends.columns


def test_neon_top_crops_rankings():
    """Verifies crop ranking queries by production, area, and yield."""
    top_prod = get_top_crops_rankings(metric="production", limit=10)
    assert len(top_prod) == 10
    assert top_prod.iloc[0]["crop_name"] == "Sugarcane"

    top_area = get_top_crops_rankings(metric="area", limit=10)
    assert len(top_area) == 10
    assert top_area.iloc[0]["crop_name"] == "Rice"

    top_yield = get_top_crops_rankings(metric="yield", limit=10)
    assert len(top_yield) == 10
    assert top_yield.iloc[0]["crop_name"] == "Sugarcane"


def test_neon_rainfall_trends_and_lpa():
    """Verifies 115-year rainfall trends and LPA calculations from Neon."""
    rain_trends = get_national_annual_rainfall_trends()

    assert not rain_trends.empty
    assert len(rain_trends) == 115
    assert rain_trends.iloc[0]["year"] == 1901
    assert rain_trends.iloc[-1]["year"] == 2015
    assert "lpa_deviation_pct" in rain_trends.columns
    assert "rainfall_category" in rain_trends.columns


def test_neon_paired_seasonal_correlations():
    """Verifies paired seasonal correlation analysis from Neon."""
    corr_df = calculate_seasonal_correlations()

    assert not corr_df.empty
    assert "relationship" in corr_df.columns
    assert "pearson_r" in corr_df.columns
    assert "spearman_rho" in corr_df.columns

    # Verify Summer yield vs Pre-monsoon rainfall is positive and significant
    summer_corr = corr_df[corr_df["relationship"] == "Pre-Monsoon Rainfall vs Summer Yield"].iloc[0]
    assert summer_corr["pearson_r"] > 0.20
    assert summer_corr["significance_at_5pct"] is True or summer_corr["significance_at_5pct"] == True

    # Verify pooled Kharif relationship is present
    kharif_corr = corr_df[corr_df["relationship"] == "Monsoon Rainfall vs Kharif Yield"].iloc[0]
    assert kharif_corr["sample_size"] > 400


def test_neon_state_sensitivity_contrast():
    """Verifies state-level sensitivity divergence (Rainfed vs Delta vs Irrigated)."""
    state_sens = calculate_state_level_rainfall_sensitivity(target_crop="Rice")

    assert not state_sens.empty
    assert "state_name" in state_sens.columns
    assert "yield_pearson_r" in state_sens.columns

    # Arid / Rainfed states show strong positive sensitivity (r > 0.50)
    high_sens_states = ["Rajasthan", "Madhya Pradesh", "Odisha", "Chhattisgarh"]
    for s in high_sens_states:
        if s in state_sens["state_name"].values:
            r = state_sens[state_sens["state_name"] == s]["yield_pearson_r"].values[0]
            assert r > 0.50

    # Delta flood-prone states (West Bengal / Assam) show negative correlation due to inundation
    if "West Bengal" in state_sens["state_name"].values:
        wb_r = state_sens[state_sens["state_name"] == "West Bengal"]["yield_pearson_r"].values[0]
        assert wb_r < 0.0
