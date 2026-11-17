"""
Visualization package for KrishiInsights.
Contains chart rendering modules for agricultural trends, meteorological figures,
and comparative agro-climatic correlation diagrams.
"""

from ml.src.visualization.agricultural_charts import (
    plot_production_area_trends,
    plot_national_yield_trend,
    plot_seasonal_distribution,
    plot_top_crops,
    plot_yield_distributions
)
from ml.src.visualization.rainfall_charts import (
    plot_long_term_rainfall_trend,
    plot_lpa_deviations,
    plot_seasonal_rainfall_breakdown,
    plot_wettest_driest_states
)
from ml.src.visualization.comparison_charts import (
    plot_rainfall_yield_scatter,
    plot_paired_correlation_heatmap,
    plot_state_sensitivity_contrast,
    plot_crop_yield_boxplots
)

__all__ = [
    "plot_production_area_trends",
    "plot_national_yield_trend",
    "plot_seasonal_distribution",
    "plot_top_crops",
    "plot_yield_distributions",
    "plot_long_term_rainfall_trend",
    "plot_lpa_deviations",
    "plot_seasonal_rainfall_breakdown",
    "plot_wettest_driest_states",
    "plot_rainfall_yield_scatter",
    "plot_paired_correlation_heatmap",
    "plot_state_sensitivity_contrast",
    "plot_crop_yield_boxplots"
]
