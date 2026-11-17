"""
Analytics package for KrishiInsights.
Contains analytical engines for EDA, crop performance, regional comparisons,
rainfall statistics, agro-climatic correlation, and outlier detection.
"""

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
    compare_states,
    get_top_producing_districts,
    compare_districts,
    calculate_state_crop_diversity
)
from ml.src.analytics.rainfall_analysis import (
    get_national_annual_rainfall_trends,
    get_rainfall_summary_statistics,
    get_state_rainfall_profile,
    get_top_wettest_and_driest_states
)
from ml.src.analytics.correlation_analysis import (
    calculate_seasonal_correlations,
    calculate_crop_rainfall_correlations,
    calculate_state_level_rainfall_sensitivity
)
from ml.src.analytics.outlier_analysis import (
    detect_outliers_iqr,
    detect_outliers_zscore,
    analyze_crop_yield_anomalies,
    analyze_rainfall_anomalies,
    classify_anomalies_summary
)

__all__ = [
    "calculate_overall_summary_statistics",
    "get_annual_production_trends",
    "get_seasonal_distribution",
    "get_yearly_record_distribution",
    "get_crop_historical_profile",
    "get_top_crops_rankings",
    "get_crop_growth_and_decline_rankings",
    "get_state_performance_summary",
    "compare_states",
    "get_top_producing_districts",
    "compare_districts",
    "calculate_state_crop_diversity",
    "get_national_annual_rainfall_trends",
    "get_rainfall_summary_statistics",
    "get_state_rainfall_profile",
    "get_top_wettest_and_driest_states",
    "calculate_seasonal_correlations",
    "calculate_crop_rainfall_correlations",
    "calculate_state_level_rainfall_sensitivity",
    "detect_outliers_iqr",
    "detect_outliers_zscore",
    "analyze_crop_yield_anomalies",
    "analyze_rainfall_anomalies",
    "classify_anomalies_summary"
]
