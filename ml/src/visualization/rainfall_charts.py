"""
Rainfall Visualization Module for KrishiInsights.

Generates meteorological figures saved to ml/reports/figures/:
- 115-year historical rainfall time series with LPA baseline and rolling averages
- Annual LPA deviation anomaly bars (excess vs drought years)
- Seasonal rainfall proportions
- Wettest and driest state comparisons
"""

import os
os.environ["MPLCONFIGDIR"] = os.path.abspath("tmp/matplotlib")

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["figure.dpi"] = 300


def plot_long_term_rainfall_trend(
    rainfall_annual_df: pd.DataFrame,
    save_path: str = "ml/reports/figures/rainfall_115yr_trend.png"
) -> str:
    """
    Plots the 115-year (1901-2015) national annual rainfall time-series
    along with the Long Period Average (LPA) line and 5-year moving average.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 6))

    years = rainfall_annual_df["year"]
    rain_col = "annual_rainfall" if "annual_rainfall" in rainfall_annual_df.columns else "national_mean_rainfall_mm"
    rain = rainfall_annual_df[rain_col]
    lpa = float(rain.mean())

    ax.plot(years, rain, color="#7ca5b8", linewidth=1.2, alpha=0.7, label="Annual Mean Rainfall (mm)")
    
    # 5-year moving average
    ma5 = rain.rolling(window=5, center=True).mean()
    ax.plot(years, ma5, color="#1b4965", linewidth=2.5, label="5-Year Moving Average")

    # LPA baseline
    ax.axhline(lpa, color="#d90429", linestyle="--", linewidth=1.8, label=f"115-Year LPA ({lpa:.1f} mm)")

    # Highlight major severe drought years
    severe_droughts = [1918, 1965, 1972, 1987, 2002, 2009]
    for dy in severe_droughts:
        if dy in years.values:
            val = rainfall_annual_df.loc[rainfall_annual_df["year"] == dy, rain_col].values[0]
            ax.scatter([dy], [val], color="#d90429", s=45, zorder=5)
            ax.annotate(f"{dy}", (dy, val), textcoords="offset points", xytext=(0, -15),
                        ha="center", fontsize=8, fontweight="bold", color="#d90429")

    ax.set_title("Long-Term Historical Rainfall Pattern in India (1901–2015)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Year", fontweight="bold")
    ax.set_ylabel("Annual Rainfall (mm)", fontweight="bold")
    ax.set_xlim(1900, 2016)
    ax.legend(loc="lower left", frameon=True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path


def plot_lpa_deviations(
    rainfall_annual_df: pd.DataFrame,
    save_path: str = "ml/reports/figures/rainfall_lpa_deviations.png"
) -> str:
    """
    Bar chart showing percentage departure from LPA (1901-2015).
    Color coded:
    - Green: Excess (> +10%)
    - Red: Deficit (Drought) (< -10%)
    - Slate: Normal (-10% to +10%)
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 5.5))

    years = rainfall_annual_df["year"]
    dev = rainfall_annual_df["lpa_deviation_pct"]

    colors = []
    for d in dev:
        if d > 10:
            colors.append("#2a9d8f")  # Excess
        elif d < -10:
            colors.append("#e63946")  # Deficit
        else:
            colors.append("#8d99ae")  # Normal

    ax.bar(years, dev, color=colors, width=0.85, edgecolor="none")
    ax.axhline(0, color="black", linewidth=1)
    ax.axhline(10, color="#2a9d8f", linestyle=":", linewidth=1, label="Excess Threshold (+10%)")
    ax.axhline(-10, color="#e63946", linestyle=":", linewidth=1, label="Deficit Threshold (-10%)")

    ax.set_title("Annual Rainfall Departure from Long Period Average (LPA) in India (1901–2015)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Year", fontweight="bold")
    ax.set_ylabel("Departure from LPA (%)", fontweight="bold")
    ax.set_xlim(1900, 2016)
    ax.legend(loc="upper left", frameon=True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path


def plot_seasonal_rainfall_breakdown(
    seasonal_data: pd.DataFrame,
    save_path: str = "ml/reports/figures/rainfall_seasonal_breakdown.png"
) -> str:
    """
    Plots the distribution of seasonal rainfall across India:
    - Southwest Monsoon (Jun-Sep)
    - Northeast Monsoon / Post-Monsoon (Oct-Dec)
    - Winter (Jan-Feb)
    - Pre-Monsoon / Summer (Mar-May)
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    seasons = ["SW Monsoon (Jun-Sep)", "Rabi / Post-Monsoon", "Pre-Monsoon (Mar-May)"]
    
    # Try different column variants
    m_col = "monsoon_rainfall_mm" if "monsoon_rainfall_mm" in seasonal_data.columns else ("monsoon_rainfall" if "monsoon_rainfall" in seasonal_data.columns else "monsoon_jjas")
    r_col = "rabi_rainfall_mm" if "rabi_rainfall_mm" in seasonal_data.columns else ("rabi_rainfall" if "rabi_rainfall" in seasonal_data.columns else "post_monsoon_ond")
    p_col = "pre_monsoon_rainfall_mm" if "pre_monsoon_rainfall_mm" in seasonal_data.columns else ("pre_monsoon_rainfall" if "pre_monsoon_rainfall" in seasonal_data.columns else "pre_monsoon_mam")

    mean_monsoon = float(seasonal_data[m_col].mean())
    mean_rabi = float(seasonal_data[r_col].mean())
    mean_pre = float(seasonal_data[p_col].mean())
    totals = [mean_monsoon, mean_rabi, mean_pre]

    colors = ["#1d3557", "#457b9d", "#a8dadc"]

    # Pie chart
    ax1.pie(totals, labels=seasons, autopct="%1.1f%%", startangle=140, colors=colors, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax1.set_title("National Seasonal Rainfall Proportion", fontweight="bold", pad=12)

    # Bar chart
    y_pos = np.arange(len(seasons))
    bars = ax2.barh(y_pos, totals, color=colors, edgecolor="black", height=0.55)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(seasons, fontweight="semibold")
    ax2.set_xlabel("Mean Rainfall (mm)", fontweight="bold")
    ax2.set_title("Average Rainfall Received per Season (mm)", fontweight="bold", pad=12)
    ax2.invert_yaxis()

    for bar in bars:
        w = bar.get_width()
        ax2.text(w + 10, bar.get_y() + bar.get_height()/2, f"{w:.1f} mm", va="center", ha="left", fontsize=9)

    plt.suptitle("Climatological Seasonal Rainfall Breakdown in India", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    return save_path


def plot_wettest_driest_states(
    states_df_or_dict,
    save_path: str = "ml/reports/figures/rainfall_wettest_driest_states.png"
) -> str:
    """
    Plots a dual-panel horizontal bar chart showing top 5 wettest and top 5 driest states.
    Accepts either a single DataFrame or a dict {"wettest": df, "driest": df}.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    if isinstance(states_df_or_dict, dict):
        wettest = states_df_or_dict["wettest"].copy()
        driest = states_df_or_dict["driest"].copy()
    else:
        rain_col = "avg_annual_rainfall" if "avg_annual_rainfall" in states_df_or_dict.columns else "mean_annual_rainfall_mm"
        wettest = states_df_or_dict.sort_values(by=rain_col, ascending=False).head(5)
        driest = states_df_or_dict.sort_values(by=rain_col, ascending=True).head(5)

    rain_col_wet = "avg_annual_rainfall" if "avg_annual_rainfall" in wettest.columns else "mean_annual_rainfall_mm"
    rain_col_dry = "avg_annual_rainfall" if "avg_annual_rainfall" in driest.columns else "mean_annual_rainfall_mm"

    # Wettest
    y_wet = np.arange(len(wettest))
    ax1.barh(y_wet, wettest[rain_col_wet], color="#1d3557", edgecolor="black")
    ax1.set_yticks(y_wet)
    ax1.set_yticklabels(wettest["state_name"], fontweight="semibold")
    ax1.set_xlabel("Mean Annual Rainfall (mm)", fontweight="bold")
    ax1.set_title("Top 5 Wettest States / Regions", fontweight="bold", color="#1d3557")
    ax1.invert_yaxis()

    # Driest
    y_dry = np.arange(len(driest))
    ax2.barh(y_dry, driest[rain_col_dry], color="#e76f51", edgecolor="black")
    ax2.set_yticks(y_dry)
    ax2.set_yticklabels(driest["state_name"], fontweight="semibold")
    ax2.set_xlabel("Mean Annual Rainfall (mm)", fontweight="bold")
    ax2.set_title("Top 5 Driest States / Regions", fontweight="bold", color="#e76f51")
    ax2.invert_yaxis()

    plt.suptitle("Regional Meteorological Contrast in India", fontsize=14, fontweight="bold", y=1.03)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    return save_path
