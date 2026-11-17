"""
Agricultural Visualization Module for KrishiInsights.

Generates high-resolution publication-grade figures saved to ml/reports/figures/:
- Production and Area historical trends
- Seasonal production distributions
- Top crop rankings (production, area, yield)
- Yield distribution histograms and KDE curves
- Crop variability comparisons
"""

import os
os.environ["MPLCONFIGDIR"] = os.path.abspath("tmp/matplotlib")

from typing import Optional, List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Apply clean professional styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["figure.dpi"] = 300


def plot_production_area_trends(
    trends_df: pd.DataFrame,
    save_path: str = "ml/reports/figures/agri_trends_production_area.png"
) -> str:
    """
    Plots historical production (Million Tonnes) and cultivated area (Million Hectares)
    over 1997-2015 with dual y-axes.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax1 = plt.subplots(figsize=(12, 6))

    year_col = "year" if "year" in trends_df.columns else "crop_year"
    prod_col = "total_production" if "total_production" in trends_df.columns else "total_production_tonnes"
    area_col = "total_area" if "total_area" in trends_df.columns else "total_area_hectares"

    years = trends_df[year_col]
    prod_mt = trends_df[prod_col] / 1e6
    area_mha = trends_df[area_col] / 1e6

    color_prod = "#2b5c8f"
    color_area = "#2a9d8f"

    ax1.set_xlabel("Crop Year", fontweight="bold")
    ax1.set_ylabel("Total Production (Million Tonnes)", color=color_prod, fontweight="bold")
    line1 = ax1.plot(years, prod_mt, color=color_prod, marker="o", linewidth=2.5, label="Production (Million Tonnes)")
    ax1.tick_params(axis="y", labelcolor=color_prod)
    ax1.set_xticks(years)
    ax1.set_xticklabels(years, rotation=45)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Total Cultivated Area (Million Hectares)", color=color_area, fontweight="bold")
    line2 = ax2.plot(years, area_mha, color=color_area, marker="s", linestyle="--", linewidth=2.5, label="Cultivated Area (Million Hectares)")
    ax2.tick_params(axis="y", labelcolor=color_area)
    ax2.grid(False)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left", frameon=True)

    plt.title("Historical Agricultural Production & Cultivated Area in India (1997–2015)", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path


def plot_national_yield_trend(
    trends_df: pd.DataFrame,
    save_path: str = "ml/reports/figures/agri_national_yield_trend.png"
) -> str:
    """
    Plots weighted national average field crop yield (Tonnes/Hectare) over 1997-2015.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.5))

    year_col = "year" if "year" in trends_df.columns else "crop_year"
    yield_col = "aggregate_yield" if "aggregate_yield" in trends_df.columns else "aggregate_field_crop_yield_tonnes_per_ha"

    years = trends_df[year_col]
    yield_val = trends_df[yield_col]

    ax.plot(years, yield_val, color="#e76f51", marker="D", linewidth=2.5, label="National Weighted Yield")
    
    # 3-year rolling mean
    rolling_yield = yield_val.rolling(window=3, min_periods=1).mean()
    ax.plot(years, rolling_yield, color="#264653", linestyle=":", linewidth=2, label="3-Year Moving Average")

    ax.set_title("Aggregate Field Crop Yield Trend in India (1997–2015)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Crop Year", fontweight="bold")
    ax.set_ylabel("Yield (Tonnes / Hectare)", fontweight="bold")
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45)
    ax.legend(loc="upper left", frameon=True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path


def plot_seasonal_distribution(
    seasonal_df: pd.DataFrame,
    save_path: str = "ml/reports/figures/agri_seasonal_distribution.png"
) -> str:
    """
    Plots a multi-panel comparison of agricultural metrics across seasons:
    - Production share (pie chart)
    - Cultivated area share (bar chart)
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    season_col = "season" if "season" in seasonal_df.columns else "season_name"
    area_col = "total_area" if "total_area" in seasonal_df.columns else "total_area_hectares"
    
    colors = ["#2b5c8f", "#e76f51", "#2a9d8f", "#e9c46a", "#f4a261", "#9d0208"]
    labels = seasonal_df[season_col]
    prod_shares = seasonal_df["production_share_pct"]
    ax1.pie(prod_shares, labels=labels, autopct="%1.1f%%", startangle=140, colors=colors[:len(labels)], wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax1.set_title("Share of Agricultural Production by Season", fontweight="bold", pad=12)

    # Horizontal bar for cultivated area
    y_pos = np.arange(len(labels))
    area_mha = seasonal_df[area_col] / 1e6
    ax2.barh(y_pos, area_mha, color="#2a9d8f", edgecolor="#1d7066", alpha=0.85)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels)
    ax2.set_xlabel("Cultivated Area (Million Hectares)", fontweight="bold")
    ax2.set_title("Cultivated Area by Season", fontweight="bold", pad=12)
    ax2.invert_yaxis()

    plt.suptitle("Seasonal Breakdown of Indian Agriculture (1997–2015)", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    return save_path


def plot_top_crops(
    ranking_df: pd.DataFrame,
    metric_col: str,
    title: str,
    xlabel: str,
    save_path: str,
    color: str = "#2b5c8f"
) -> str:
    """
    Horizontal bar chart for top crop rankings.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    top10 = ranking_df.head(10).sort_values(by=metric_col, ascending=True)
    y_pos = np.arange(len(top10))

    bars = ax.barh(y_pos, top10[metric_col], color=color, edgecolor="black", alpha=0.85, height=0.65)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top10["crop_name"], fontweight="semibold")
    ax.set_xlabel(xlabel, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)

    # Annotate bar values
    for bar in bars:
        width = bar.get_width()
        ax.text(width * 1.01, bar.get_y() + bar.get_height()/2, f"{width:,.1f}",
                va="center", ha="left", fontsize=9, color="#222222")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path


def plot_yield_distributions(
    df: pd.DataFrame,
    crops: List[str] = ["Rice", "Wheat", "Sugarcane", "Maize"],
    save_path: str = "ml/reports/figures/agri_yield_distributions.png"
) -> str:
    """
    Multi-panel KDE and histogram plot for key crop yield distributions.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    axes = axes.flatten()

    crop_col = "crop_name" if "crop_name" in df.columns else "crop"
    yield_col = "yield_amount" if "yield_amount" in df.columns else "yield"

    palette = ["#2b5c8f", "#e76f51", "#2a9d8f", "#e9c46a"]

    for i, crop in enumerate(crops):
        ax = axes[i]
        crop_data = df[df[crop_col].str.lower() == crop.lower()][yield_col].dropna()
        
        # Filter extreme outliers for clean distribution visualization
        q99 = crop_data.quantile(0.99)
        filtered = crop_data[crop_data <= q99]

        sns.histplot(filtered, kde=True, ax=ax, color=palette[i % len(palette)], bins=30, edgecolor="white", alpha=0.6)
        mean_val = float(filtered.mean())
        median_val = float(filtered.median())

        ax.axvline(mean_val, color="red", linestyle="--", linewidth=1.5, label=f"Mean: {mean_val:.2f}")
        ax.axvline(median_val, color="green", linestyle="-.", linewidth=1.5, label=f"Median: {median_val:.2f}")
        
        ax.set_title(f"{crop} Yield Distribution (Tonnes/Ha)", fontweight="bold")
        ax.set_xlabel("Yield (Tonnes/Hectare)")
        ax.set_ylabel("Frequency")
        ax.legend(loc="upper right", frameon=True)

    plt.suptitle("Empirical Yield Distributions for Major Indian Crops (1997–2015)", fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path
