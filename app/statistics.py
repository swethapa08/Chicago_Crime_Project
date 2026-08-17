# ============================================================================
# USE CASE 3: STATISTICAL INSIGHTS & PATTERN DETECTION
# ============================================================================
# This module provides statistical analysis functions for detecting patterns,
# outliers, and correlations in crime data. Functions focus on:
# - Crime Intensity by Time (hourly distribution)
# - Community Area Clusters & Outlier Detection (using IQR method)
# - Crime Cross-Correlation (numeric features correlation matrix)
# - Descriptive Statistics
# ============================================================================

import pandas as pd
import numpy as np
import sqlite3

from .config import Config
from .ingestion import load_csv
from .analysis import find_column, clean_dataframe


def get_connection():
    return sqlite3.connect(Config.DATABASE_PATH)


def load_data():
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM crimes", conn)
    finally:
        conn.close()
    if df.empty:
        raise ValueError("Crime database is empty. Click Load Dataset first.")
    return df


def get_statistical_data():

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

    community_col = find_column(
        df,
        [
            "community_area",
            "community"
        ]
    )

    if date_col:

        df["_date"] = pd.to_datetime(
            df[date_col],
            errors="coerce"
        )

        df["_hour"] = (
            df["_date"].dt.hour
        )

        df["_day"] = (
            df["_date"].dt.day
        )

        df["_weekday"] = (
            df["_date"].dt.day_name()
        )

    return df, community_col


def hourly_statistics():

    df, _ = get_statistical_data()

    if "_hour" not in df.columns:
        return []

    result = (
        df["_hour"]
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
    )

    return [
        {
            "hour": int(hour),
            "count": int(count)
        }
        for hour, count in result.items()
    ]


def peak_hour():

    data = hourly_statistics()

    if not data:
        return {
            "hour": None,
            "count": 0
        }

    item = max(
        data,
        key=lambda x: x["count"]
    )

    return item


def community_statistics():

    df, community_col = (
        get_statistical_data()
    )

    if not community_col:
        return []

    grouped = (
        df.groupby(
            community_col
        )
        .size()
        .reset_index(
            name="crime_count"
        )
    )

    grouped["crime_count"] = (
        pd.to_numeric(
            grouped["crime_count"],
            errors="coerce"
        )
    )

    return (
        grouped
        .sort_values(
            "crime_count",
            ascending=False
        )
        .head(20)
        .to_dict(
            orient="records"
        )
    )


def numerical_statistics():

    df, _ = get_statistical_data()

    numeric = df.select_dtypes(
        include=np.number
    )

    if numeric.empty:
        return []

    result = (
        numeric
        .describe()
        .transpose()
        .reset_index()
        .rename(
            columns={
                "index": "column"
            }
        )
    )

    result = result.replace(
        {np.nan: None}
    )

    return result.to_dict(
        orient="records"
    )


def iqr_outliers():
    """
    Identify outliers using the Interquartile Range (IQR) method.
    Outliers are values that fall below Q1 - 1.5*IQR or above Q3 + 1.5*IQR
    """

    df, _ = get_statistical_data()

    numeric = df.select_dtypes(
        include=np.number
    )

    result = []

    for column in numeric.columns:

        series = (
            pd.to_numeric(
                numeric[column],
                errors="coerce"
            )
            .dropna()
        )

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        count = int(
            (
                (series < lower) |
                (series > upper)
            ).sum()
        )

        result.append({
            "column": column,
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(lower),
            "upper_bound": float(upper),
            "outliers": count
        })

    return result


def community_area_outliers():
    """
    Identify community areas with crime counts that are statistical outliers
    using the IQR method. Returns community areas with unusually high or low crime.
    """
    df = clean_dataframe(load_data())
    
    community_counts = df[df["community_area"] != "Unknown"]["community_area"].value_counts()
    
    if len(community_counts) == 0:
        return {
            "q1": 0, "q3": 0, "iqr": 0,
            "lower_bound": 0, "upper_bound": 0,
            "outliers": []
        }
    
    q1 = community_counts.quantile(0.25)
    q3 = community_counts.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    
    outlier_areas = community_counts[(community_counts > upper) | (community_counts < lower)]
    
    return {
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_bound": float(lower),
        "upper_bound": float(upper),
        "outliers": [
            {"community_area": str(area), "crime_count": int(count)}
            for area, count in outlier_areas.items()
        ]
    }


def correlation_matrix():
    """
    Calculate correlation matrix of numeric features in the crime dataset.
    Shows relationships between Year, Month, Hour, Arrest, and Domestic fields.
    """

    df, _ = get_statistical_data()

    numeric = df.select_dtypes(
        include=np.number
    )

    if numeric.empty:
        return {
            "columns": [],
            "values": []
        }

    correlation = (
        numeric
        .corr()
        .replace({
            np.nan: 0
        })
    )

    return {
        "columns": list(
            correlation.columns
        ),
        "values": correlation.values.tolist()
    }


def run_use_case_3():

    print("\n")
    print("=" * 80)
    print("USE CASE 3 - STATISTICAL ANALYSIS")
    print("=" * 80)

    peak = peak_hour()

    if peak["hour"] is not None:

        print(
            f"\nPeak crime hour: "
            f"{peak['hour']:02d}:00"
        )

        print(
            f"Crime count: "
            f"{peak['count']:,}"
        )

    print("\nIQR OUTLIER ANALYSIS")

    for item in iqr_outliers():

        print(
            f"{item['column']}: "
            f"{item['outliers']} outliers"
        )

    print("\nDESCRIPTIVE STATISTICS")

    statistics = numerical_statistics()

    if statistics:

        print(
            pd.DataFrame(
                statistics
            ).to_string(
                index=False
            )
        )

    return {
        "hourly": hourly_statistics(),
        "peak_hour": peak,
        "community_statistics":
            community_statistics(),
        "community_outliers":
            community_area_outliers(),
        "descriptive":
            numerical_statistics(),
        "iqr":
            iqr_outliers(),
        "correlation":
            correlation_matrix()
    }