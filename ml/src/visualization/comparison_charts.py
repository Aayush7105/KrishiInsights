"""
Comparative and Correlation Visualization Module for KrishiInsights.

Generates analytical synthesis figures saved to ml/reports/figures/:
- Rainfall vs Crop Yield scatter plots with linear trendlines and stats annotations
- Correlation heatmaps for paired seasonal metrics (Pearson r and Spearman rho)
- State sensitivity contrasts (irrigated vs rainfed states)
- Crop yield outlier boxplots
"""

import os
os.environ["MPLCONFIGDIR"] = os.path.abspath("tmp/matplotlib")

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["figure.dpi"] = 300


def plot_rainfall_yield_scatter(
    aligned_df: pd.DataFrame,
    crop_name: str = "Rice",
    rainfall_col: str = "monsoon_rainfall_mm",
    season_name: str = "Kharif",
    save_path: str = "ml/reports/figures/correlation_rice_monsoon_scatter.png"
) -> str:
    """
    Scatter plot of seasonal rainfall vs crop yield with OLS linear regression fit line
    and annotated Pearson r and p-values.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    crop_c = "crop_name" if "crop_name" in aligned_df.columns else "crop"
    season_c = "season" if "season" in aligned_df.columns else "season_name"
    year_c = "year" if "year" in aligned_df.columns else "crop_year"
    yield_c = "yield_amount" if "yield_amount" in aligned_df.columns else "yield"
    
    # Resolve rainfall column
    if rainfall_col not in aligned_df.columns:
        if "monsoon_rainfall_mm" in aligned_df.columns:
            rainfall_col = "monsoon_rainfall_mm"
        elif "monsoon_jjas" in aligned_df.columns:
            rainfall_col = "monsoon_jjas"
        elif "annual_rainfall_mm" in aligned_df.columns:
            rainfall_col = "annual_rainfall_mm"

    # Filter data
    subset = aligned_df[
        (aligned_df[crop_c].str.lower() == crop_name.lower()) &
        (aligned_df[season_c].str.lower() == season_name.lower())
    ].dropna(subset=[rainfall_col, yield_c])

    # Aggregate by state and year for clean relationship view
    grouped = subset.groupby([year_c, "state_name"]).agg({
        rainfall_col: "mean",
        "production": "sum",
        "area": "sum"
    }).reset_index()
    grouped["yield"] = grouped["production"] / grouped["area"]
    grouped = grouped[grouped["yield"] < 15]  # Filter extreme artifacts

    x = grouped[rainfall_col]
    y = grouped["yield"]

    if len(x) > 5:
        # Compute regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        line = slope * x + intercept

        ax.scatter(x, y, color="#2b5c8f", alpha=0.45, edgecolors="none", s=40, label="State-Year Observation")
        ax.plot(x, line, color="#e63946", linewidth=2.2, label=f"Fit (r = {r_value:.2f}, p = {p_value:.3e})")

        ax.text(0.05, 0.90, f"Pearson r: {r_value:.3f}\nSlope: {slope*1000:.3f} T/Ha per 1000mm\np-value: {p_value:.3e}",
                transform=ax.transAxes, fontsize=10, verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#cccccc", alpha=0.9))

    ax.set_title(f"Relationship: {season_name} {crop_name} Yield vs {rainfall_col.replace('_', ' ').title()}",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel(f"{rainfall_col.replace('_', ' ').title()} (mm)", fontweight="bold")
    ax.set_ylabel(f"{crop_name} Yield (Tonnes / Hectare)", fontweight="bold")
    ax.legend(loc="lower right", frameon=True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path


def plot_paired_correlation_heatmap(
    correlation_matrix_data: pd.DataFrame,
    save_path: str = "ml/reports/figures/correlation_paired_heatmap.png"
) -> str:
    """
    Heatmap displaying Pearson and Spearman correlation coefficients across
    agricultural seasons and paired rainfall metrics.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 6))

    sns.heatmap(
        correlation_matrix_data,
        annot=True,
        fmt=".3f",
        cmap="vlag",
        vmin=-0.5,
        vmax=0.5,
        center=0,
        cbar_kws={"label": "Correlation Coefficient"},
        linewidths=1.2,
        linecolor="white",
        ax=ax
    )

    ax.set_title("Agro-Climatic Correlation Matrix: Rainfall vs Crop Performance", fontsize=12, fontweight="bold", pad=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path


def plot_state_sensitivity_contrast(
    state_sensitivity_df: pd.DataFrame,
    save_path: str = "ml/reports/figures/correlation_state_sensitivity_contrast.png"
) -> str:
    """
    Contrasting bar chart illustrating rainfall sensitivity between
    intensively irrigated states (e.g. Punjab, Haryana) and rainfed states (e.g. Odisha, Bihar, Rajasthan).
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.5))

    r_col = "yield_pearson_r" if "yield_pearson_r" in state_sensitivity_df.columns else ("pearson_r" if "pearson_r" in state_sensitivity_df.columns else "correlation")
    sorted_df = state_sensitivity_df.sort_values(by=r_col, ascending=True)
    y_pos = np.arange(len(sorted_df))

    colors = ["#e76f51" if r < 0.2 else "#2a9d8f" for r in sorted_df[r_col]]

    bars = ax.barh(y_pos, sorted_df[r_col], color=colors, edgecolor="black", height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_df["state_name"], fontweight="semibold")
    ax.set_xlabel("Pearson Correlation Coefficient (r) with Annual Rainfall", fontweight="bold")
    ax.set_title("Rainfall Sensitivity Contrast Across Indian States", fontsize=13, fontweight="bold", pad=12)
    ax.axvline(0, color="black", linewidth=0.8)

    for bar in bars:
        w = bar.get_width()
        offset = 0.02 if w >= 0 else -0.06
        ax.text(w + offset, bar.get_y() + bar.get_height()/2, f"{w:.2f}",
                va="center", ha="left" if w >= 0 else "right", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path


def plot_crop_yield_boxplots(
    df: pd.DataFrame,
    crops: list = ["Rice", "Wheat", "Maize", "Cotton(lint)", "Jowar", "Bajra"],
    save_path: str = "ml/reports/figures/outliers_crop_yield_boxplots.png"
) -> str:
    """
    Boxplot showing yield distribution and outlier points for major Indian crops.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))

    crop_c = "crop_name" if "crop_name" in df.columns else "crop"
    yield_c = "yield_amount" if "yield_amount" in df.columns else "yield"

    # Filter selected crops and exclude coconut
    subset = df[df[crop_c].isin(crops)].copy()
    
    # Clip for clean boxplot view (yield < 10)
    subset = subset[subset[yield_c] <= 10]

    palette = sns.color_palette("Set2", len(crops))
    sns.boxplot(
        x=crop_c,
        y=yield_c,
        data=subset,
        order=crops,
        hue=crop_c,
        palette=palette,
        legend=False,
        fliersize=3,
        linewidth=1.2,
        ax=ax
    )

    ax.set_title("Yield Distributions & Outlier Points for Major Field Crops (Tonnes/Ha)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Crop Name", fontweight="bold")
    ax.set_ylabel("Yield (Tonnes / Hectare)", fontweight="bold")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path
