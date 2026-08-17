# ============================================================================
# VISUALIZATION & CHARTS - ALL USE CASES
# ============================================================================
# This module provides chart creation functions for all use cases:
#
# USE CASE 1: Data Ingestion (N/A - handled in ingestion.py)
#
# USE CASE 2: Exploratory Analysis & Visualization
#   - create_yearly_chart()                    - Crime trend over years
#   - create_top_crimes_chart()                - Crime distribution by category
#   - create_top_community_areas_chart()       - Top 10 community areas
#   - create_crime_heatmap()                   - Heatmap by month & day of week
#   - create_yearly_arrest_rate_chart()        - Arrests and crime outcomes
#
# USE CASE 3: Statistical Insights & Pattern Detection
#   - create_hourly_chart()                    - Crime intensity by time
#   - create_case3_outlier_boxplot_chart()     - Community area outliers (IQR)
#   - create_case3_correlation_heatmap_chart() - Numeric feature correlations
#
# USE CASE 4: MySQL Reporting & Integration
#   - create_mysql_reporting_visualizations()  - MySQL view-based charts
#   - create_all_visualizations()              - Combined visualization pipeline
# ============================================================================

import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from .config import Config
from .ingestion import load_csv
from .analysis import (
    find_column,
    yearly_trend,
    crime_summary,
    load_data,
    clean_dataframe
)
from .statistics import hourly_statistics
from .database import get_connection


def ensure_output_directory():
    os.makedirs(
        Config.CHARTS_DIR,
        exist_ok=True
    )


def save_figure(filename):

    ensure_output_directory()

    path = os.path.join(
        Config.CHARTS_DIR,
        filename
    )

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    return path


def create_yearly_chart():

    data = yearly_trend()

    if not data:
        return None

    df = pd.DataFrame(data)

    plt.figure(
        figsize=(10, 5)
    )

    sns.lineplot(
        data=df,
        x="year",
        y="count",
        marker="o"
    )

    plt.title(
        "Crime Trend Over Years"
    )

    plt.xlabel("Year")
    plt.ylabel("Total Number of Crimes")

    return save_figure("01_crimes_by_year.png")


def create_top_crimes_chart():

    summary = crime_summary()

    data = summary["top_crimes"]

    if not data:
        return None

    df = pd.DataFrame(data)

    df = df.sort_values(
        "count",
        ascending=True
    )
    total = df["count"].sum()
    df["percentage"] = ((df["count"] / total) * 100).round(2) if total else 0

    plt.figure(
        figsize=(10, 6)
    )

    bars = plt.barh(
        df["crime"],
        df["count"],
        color="#60a5fa"
    )

    for bar, value, pct in zip(bars, df["count"], df["percentage"]):
        plt.text(
            value + 10,
            bar.get_y() + bar.get_height() / 2,
            f"{value} ({pct:.2f}%)",
            va="center",
            ha="left",
            fontsize=8,
            color="#dbeafe"
        )

    # Keep a clearly visible proportion annotation for the top-crime chart.
    if "percentage" in df.columns:
        for _, row in df.iterrows():
            plt.text(
                row["count"] / 2,
                df.index.get_loc(_) + 0.5,
                f"{row['percentage']:.2f}%",
                va="center",
                ha="center",
                fontsize=8,
                color="white",
                fontweight="bold"
            )

    plt.title(
        "Crime Distribution by Category"
    )

    plt.xlabel(
        "Number of Crimes"
    )

    plt.ylabel("Crime Category")

    return save_figure("02_top10_categories.png")


def create_hourly_chart():

    data = hourly_statistics()

    if not data:
        return None

    df = pd.DataFrame(data)

    plt.figure(
        figsize=(11, 5)
    )

    sns.barplot(
        data=df,
        x="hour",
        y="count"
    )

    plt.title("Crime Intensity by Time")

    plt.xlabel(
        "Hour of Day"
    )

    plt.ylabel(
        "Number of Crimes"
    )

    return save_figure("06_crimes_by_hour.png")


def create_crime_heatmap():

    df = load_csv(
        Config.CRIME_CSV
    )

    date_col = find_column(
        df,
        [
            "date",
            "crime_date",
            "datetime"
        ]
    )

    if date_col:
        df["_date"] = pd.to_datetime(
            df[date_col],
            errors="coerce"
        )

    month_col = "_month" if date_col else find_column(df, ["month", "crime_month"])
    day_col = "_day_of_week" if date_col else find_column(df, ["day_of_week", "weekday", "dayofweek"])

    if date_col:
        df[month_col] = df["_date"].dt.month
        df[day_col] = df["_date"].dt.day_name()

    if month_col is None or day_col is None:
        return None

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    pivot = (
        df.groupby(
            [month_col, day_col],
            dropna=False
        )
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=range(1, 13),
            columns=day_order,
            fill_value=0
        )
    )

    if pivot.empty:
        return None

    plt.figure(
        figsize=(12, 7)
    )

    sns.heatmap(
        pivot,
        cmap="YlOrRd",
        linewidths=0.3,
        annot=False
    )

    plt.title(
        "Heatmap of Crime by Month and Day of Week"
    )

    plt.xlabel("Day of Week")
    plt.ylabel("Month")

    return save_figure("04_month_day_heatmap.png")


def create_correlation_heatmap():

    df = load_csv(
        Config.CRIME_CSV
    )

    numeric = df.select_dtypes(
        include="number"
    )

    if numeric.shape[1] < 2:
        return None

    correlation = numeric.corr()

    plt.figure(
        figsize=(12, 9)
    )

    sns.heatmap(
        correlation,
        annot=False,
        cmap="coolwarm",
        center=0
    )

    plt.title(
        "Numeric Feature Correlation Heatmap"
    )

    return save_figure("08_correlation_heatmap.png")


def create_top_community_areas_chart():

    df = load_csv(Config.CRIME_CSV)

    if "community_area" not in df.columns:
        community_col = find_column(df, ["community_area", "community", "community_code"])
        if community_col is None:
            return None
    else:
        community_col = "community_area"

    top = (
        df[community_col]
        .dropna()
        .astype(str)
        .value_counts()
        .head(10)
        .reset_index()
    )

    if top.empty:
        return None

    top.columns = ["community_area", "count"]

    top = top.sort_values("count", ascending=True)

    plt.figure(figsize=(11, 7))
    plt.barh(top["community_area"], top["count"], color="steelblue")
    plt.title("Top 10 Community Areas by Crime Count")
    plt.xlabel("Crime Count")
    plt.ylabel("Community Area")

    return save_figure("05_top10_communities.png")


def create_yearly_arrest_rate_chart():

    df = load_data()  # Load from database, not CSV
    if "Year" not in df.columns:
        return None

    yearly = (
        df.groupby("Year")
        .apply(lambda g: (g["arrest"].fillna(False).astype(str).str.lower().isin(["true", "1", "yes", "y", "t"]).astype(int).sum() / len(g) * 100) if "arrest" in g.columns else 0)
        .reset_index(name="arrest_rate")
    )
    if yearly.empty:
        return None

    yearly.columns = ["Year", "arrest_rate"]
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=yearly, x="Year", y="arrest_rate", marker="o")
    plt.title("Yearly Arrest Rate")
    plt.xlabel("Year")
    plt.ylabel("Arrest Rate (%)")
    return save_figure("03_arrest_rate_by_year.png")


def create_arrests_by_crime_type_chart():

    df = load_csv(Config.CRIME_CSV)
    if "arrest" not in df.columns or "primary_type" not in df.columns:
        return None

    arrests = (
        df.groupby("primary_type")["arrest"]
        .apply(lambda s: s.fillna(False).astype(str).str.lower().isin(["true", "1", "yes", "y", "t"]).astype(int).sum())
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    arrests.columns = ["crime_type", "arrests"]
    if arrests.empty:
        return None

    plt.figure(figsize=(10, 6))
    sns.barplot(data=arrests, x="arrests", y="crime_type")
    plt.title("Arrests by Crime Type")
    plt.xlabel("Number of Arrests")
    plt.ylabel("Crime Type")
    return save_figure("arrests_by_crime_type.png")


def create_monthly_crime_frequency_chart():

    df = load_csv(Config.CRIME_CSV)
    if "date" not in df.columns:
        return None

    df = df.copy()
    df["_date"] = pd.to_datetime(df["date"], errors="coerce")
    monthly = df["_date"].dt.month.value_counts().sort_index().reset_index()
    monthly.columns = ["month", "crime_count"]
    plt.figure(figsize=(10, 5))
    sns.barplot(data=monthly, x="month", y="crime_count")
    plt.title("Monthly Crime Frequency")
    plt.xlabel("Month")
    plt.ylabel("Crime Count")
    return save_figure("monthly_crime_frequency.png")


def create_case3_hourly_intensity_chart():

    df = load_csv(Config.CRIME_CSV)
    if "date" not in df.columns:
        return None

    df = df.copy()
    df["_date"] = pd.to_datetime(df["date"], errors="coerce")
    hourly = df["_date"].dt.hour.value_counts().sort_index().reset_index()
    hourly.columns = ["hour", "crime_count"]

    plt.figure(figsize=(11, 5))
    sns.lineplot(data=hourly, x="hour", y="crime_count", marker="o")
    plt.title("Crime Intensity by Time")
    plt.xlabel("Hour of Day")
    plt.ylabel("Number of Crimes")
    return save_figure("06_crimes_by_hour.png")


def create_case3_outlier_boxplot_chart():
    # Use the cleaned database so community_code has the same normalized name
    # used by the API and by the IQR calculation.
    df = load_data()
    community_col = find_column(df, ["community_code", "community_area", "community"])
    
    if community_col is None or community_col not in df.columns:
        return None

    community_counts = df[community_col].dropna().astype(str).value_counts().reset_index()
    community_counts.columns = ["community_code", "crime_count"]

    # Calculate quartiles and bounds for annotation
    q1 = community_counts["crime_count"].quantile(0.25)
    q3 = community_counts["crime_count"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    plt.figure(figsize=(10, 5))
    sns.boxplot(data=community_counts, x="crime_count")
    
    # Add text annotations for bounds
    plt.axvline(lower_bound, color='red', linestyle='--', linewidth=1.5, label=f'Lower Bound: {lower_bound:.2f}')
    plt.axvline(upper_bound, color='orange', linestyle='--', linewidth=1.5, label=f'Upper Bound: {upper_bound:.2f}')
    
    plt.title("Community Area Crime Count Outliers")
    plt.xlabel("Crime Count")
    plt.legend(loc='upper right')
    return save_figure("07_community_boxplot.png")


def create_case3_correlation_heatmap_chart():
    df = clean_dataframe(load_data())
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return None

    corr = numeric.corr().round(3)
    plt.figure(figsize=(max(10, numeric.shape[1] * 0.85), max(8, numeric.shape[1] * 0.7)))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0)
    plt.title("All Numeric Crime Features: Cross-Correlation Heatmap")
    return save_figure("08_correlation_heatmap.png")


def create_mysql_reporting_visualizations():
    """Create separate, clearly named charts from the reporting SQL views."""
    conn = get_connection()
    try:
        yearly = pd.read_sql_query(
            "SELECT * FROM vw_crime_yearly ORDER BY year", conn
        )
        categories = pd.read_sql_query(
            "SELECT * FROM vw_crime_by_category ORDER BY crime_count DESC", conn
        )
    finally:
        conn.close()

    result = {}
    if not yearly.empty:
        plt.figure(figsize=(10, 5))
        yearly_column = "Year" if "Year" in yearly.columns else "year"
        sns.lineplot(data=yearly, x=yearly_column, y="crime_count", marker="o")
        plt.title("MySQL View: Crime Count per Year")
        plt.xlabel("Year")
        plt.ylabel("Crime Count")
        result["mysql_crimes_by_year"] = save_figure("09_mysql_crimes_by_year.png")

    if not categories.empty:
        plt.figure(figsize=(10, 5))
        sns.barplot(data=categories, x="crime_count", y="crime_type")
        plt.title("MySQL View: Top 5 Crime Types")
        plt.xlabel("Crime Count")
        plt.ylabel("Crime Type")
        result["mysql_top5_crime_types"] = save_figure("10_mysql_top5_crime_types.png")

    return result


def create_all_visualizations():

    result = {
        "crime_trend_over_years":
            create_yearly_chart(),

        "crime_distribution_by_category":
            create_top_crimes_chart(),

        "crimes_by_hour":
            create_hourly_chart(),

        "month_day_heatmap":
            create_crime_heatmap(),

        "top10_communities":
            create_top_community_areas_chart(),

        "arrest_rate_by_year":
            create_yearly_arrest_rate_chart(),

        "arrests_by_crime_type":
            create_arrests_by_crime_type_chart(),

        "crimes_by_hour":
            create_case3_hourly_intensity_chart(),

        "community_boxplot":
            create_case3_outlier_boxplot_chart(),

        "correlation_heatmap":
            create_case3_correlation_heatmap_chart(),

        **create_mysql_reporting_visualizations()
    }

    return result


if __name__ == "__main__":

    results = create_all_visualizations()

    for name, path in results.items():

        print(
            f"{name}: {path}"
        )
