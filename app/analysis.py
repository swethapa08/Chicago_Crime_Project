import sqlite3
import numpy as np
import pandas as pd

from .config import Config


def get_connection():
    return sqlite3.connect(
        Config.DATABASE_PATH
    )


def load_data():

    conn = get_connection()

    try:
        df = pd.read_sql(
            "SELECT * FROM crimes",
            conn
        )
    finally:
        conn.close()

    if df.empty:
        raise ValueError(
            "Crime database is empty. Click Load Dataset first."
        )

    return df


def clean_dataframe(df):

    # Handle Year column (capitalized from engineered feature)
    compatibility_aliases = {
        "community_code": "community_area",
        "district_code": "district",
        "iucr_code": "iucr",
        "location_desc": "location_description",
    }
    for source, alias in compatibility_aliases.items():
        if source in df.columns and alias not in df.columns:
            df[alias] = df[source]

    if "year" in df.columns and "Year" not in df.columns:
        df["Year"] = df["year"]

    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(
            df["Year"],
            errors="coerce"
        ).fillna(-1).astype(int)

    # Handle Month column (capitalized from engineered feature)
    if "Month" in df.columns:
        df["Month"] = pd.to_numeric(
            df["Month"],
            errors="coerce"
        ).fillna(-1).astype(int)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    if "Hour" in df.columns:
        df["Hour"] = pd.to_numeric(
            df["Hour"],
            errors="coerce"
        ).fillna(-1).astype(int)
    elif "date" in df.columns:
        df["Hour"] = (
            df["date"]
            .dt.hour
            .fillna(-1)
            .astype(int)
        )

    df["arrest"] = pd.to_numeric(
        df["arrest"],
        errors="coerce"
    ).fillna(-1).astype(int)

    df["domestic"] = pd.to_numeric(
        df["domestic"],
        errors="coerce"
    ).fillna(-1).astype(int)

    for col in [
        "primary_type",
        "community_area",
        "district",
        "iucr",
        "fbi_code"
    ]:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
            )

    return df


def find_column(df, candidate_names):
    for candidate in candidate_names:
        if candidate in df.columns:
            return candidate

    lowercase_map = {
        str(column).lower(): column
        for column in df.columns
    }

    for candidate in candidate_names:
        if str(candidate).lower() in lowercase_map:
            return lowercase_map[str(candidate).lower()]

    return None


def crime_summary():
    df = clean_dataframe(load_data())

    total_crimes = int(len(df))
    arrests = int(df["arrest"].sum())
    unique_crime_types = int(df["primary_type"].nunique())
    arrest_rate = round(
        (arrests / total_crimes * 100),
        2
    ) if total_crimes else 0

    top_crimes = (
        df["primary_type"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_crimes.columns = ["crime", "count"]
    top_crimes["percentage"] = (
        top_crimes["count"] / total_crimes * 100
    ).round(2) if total_crimes else 0

    return {
        "total_crimes": total_crimes,
        "unique_crime_types": unique_crime_types,
        "arrests": arrests,
        "arrest_rate": arrest_rate,
        "top_crimes": [
            {
                "crime": row["crime"],
                "count": int(row["count"]),
                "percentage": float(row["percentage"])
            }
            for _, row in top_crimes.iterrows()
        ]
    }


def yearly_trend():
    df = clean_dataframe(load_data())
    yearly = (
        df[df["Year"] > 0]
        .groupby("Year")
        .size()
        .reset_index(name="count")
    )

    return [
        {
            "year": int(row["Year"]),
            "count": int(row["count"])
        }
        for _, row in yearly.iterrows()
    ]


def top_communities():
    df = clean_dataframe(load_data())
    communities = (
        df[df["community_area"] != "Unknown"]
        ["community_area"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    communities.columns = ["community_area", "count"]

    return [
        {
            "community_area": str(row["community_area"]),
            "count": int(row["count"])
        }
        for _, row in communities.iterrows()
    ]


def crime_by_district():
    df = clean_dataframe(load_data())
    districts = (
        df[df["district"] != "Unknown"]
        ["district"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    districts.columns = ["district", "count"]

    return [
        {
            "district": str(row["district"]),
            "count": int(row["count"])
        }
        for _, row in districts.iterrows()
    ]


# =========================================================
# DASHBOARD
# =========================================================

def get_statistics():

    df = clean_dataframe(load_data())

    total = len(df)

    arrests = int(df["arrest"].sum())

    domestic = int(
        df["domestic"].sum()
    )

    arrest_rate = (
        round(arrests / total * 100, 2)
        if total else 0
    )

    yearly = (
        df[df["Year"] > 0]
        .groupby("Year")
        .size()
        .reset_index(name="count")
    )

    categories = (
        df["primary_type"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    categories.columns = [
        "label",
        "count"
    ]

    communities = (
        df[df["community_area"] != "Unknown"]
        ["community_area"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    communities.columns = [
        "label",
        "count"
    ]

    top_category = (
        categories.iloc[0]["label"]
        if not categories.empty else "Unknown"
    )

    result = {
        "status": "success",

        "kpis": {
            "total_crimes": total,
            "arrests": arrests,
            "domestic_cases": domestic,
            "arrest_rate": arrest_rate
        },

        "yearly": {
            "labels": yearly["Year"].astype(str).tolist(),
            "values": yearly["count"].astype(int).tolist()
        },

        "categories": {
            "labels": categories["label"].tolist(),
            "values": categories["count"].astype(int).tolist()
        },

        "communities": {
            "labels": communities["label"].tolist(),
            "values": communities["count"].astype(int).tolist()
        },

        "arrests_chart": {
            "labels": ["Arrest", "No Arrest"],
            "values": [
                arrests,
                total - arrests
            ]
        }
    }

    result["executive_summary"] = (
        "The dataset contains "
        f"{total} recorded crimes. "
        f"{arrests} arrests were made, which gives an arrest rate of {arrest_rate}%. "
        f"The most common crime category is {top_category}. "
        "This overview helps identify the city’s dominant crime patterns and arrest behavior."
    )

    result["questions_answered"] = [
        "What is the total scale of crime in Chicago?",
        "What percentage of incidents result in an arrest?",
        "Which crime type appears most often?",
        "Which communities report the highest crime volumes?"
    ]

    return result


# =========================================================
# CASE 1
# =========================================================

def case1_crime_type_analysis():

    df = clean_dataframe(load_data())

    counts = (
        df["primary_type"]
        .value_counts()
    )

    total = len(df)

    top10 = (
        counts
        .head(10)
        .reset_index()
    )

    top10.columns = [
        "label",
        "count"
    ]

    top10["percentage"] = (
        top10["count"]
        / total
        * 100
    ).round(2)

    result = {
        "status": "success",

        "kpis": {
            "unique_crime_types": int(
                counts.size
            ),
            "most_common_crime": (
                counts.index[0]
                if len(counts)
                else "Unknown"
            ),
            "most_common_count": int(
                counts.iloc[0]
                if len(counts)
                else 0
            ),
            "top_crime_share": round(
                (
                    counts.iloc[0]
                    / total
                    * 100
                ),
                2
            ) if total else 0
        },

        "top10": {
            "labels": top10["label"].tolist(),
            "values": top10["count"].astype(int).tolist()
        },

        "percentage": {
            "labels": top10["label"].tolist(),
            "values": top10["percentage"].tolist()
        },

        "table": [
            {
                "crime": row["label"],
                "count": int(row["count"]),
                "percentage": float(
                    row["percentage"]
                )
            }
            for _, row in top10.iterrows()
        ]
    }

    result["summary"] = (
        "Use Case 1 focuses on what the most common crime category is and how the crime profile is distributed. "
        f"The dataset contains {len(top10)} key categories in the top section, and {counts.size} unique crime types in total. "
        f"The most frequent category is {result['kpis']['most_common_crime']} with {result['kpis']['most_common_count']} incidents, "
        f"which accounts for {result['kpis']['top_crime_share']}% of all reported crimes."
    )

    result["questions_answered"] = [
        "Which crime category is most frequent?",
        "How many unique crime types are present in the dataset?",
        "What percentage does the top crime category contribute to the total?",
        "How are the other major crimes distributed across the dataset?"
    ]

    return result


# =========================================================
# CASE 2
# =========================================================

def case2_arrest_analysis():

    df = clean_dataframe(load_data())

    yearly_counts = (
        df[df["Year"] > 0]
        .groupby("Year")
        .size()
        .reset_index(name="crime_count")
    )

    top_categories = (
        df["primary_type"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_categories.columns = ["crime_category", "count"]
    top_categories["percentage"] = (
        top_categories["count"] / len(df) * 100
    ).round(2)

    total = len(df)
    arrests = int(df["arrest"].sum())
    arrest_rate = (arrests / total * 100) if total else 0

    yearly = (
        df[df["Year"] > 0]
        .groupby("Year")
        .agg(
            total_crimes=("arrest", "size"),
            arrests=("arrest", "sum")
        )
        .reset_index()
    )

    yearly["rate"] = (
        yearly["arrests"] / yearly["total_crimes"] * 100
    ).round(2)

    if len(yearly):
        highest = yearly.loc[yearly["rate"].idxmax()]
        highest_year = int(highest["Year"])
        highest_rate = float(highest["rate"])
    else:
        highest_year = 0
        highest_rate = 0

    year_overview = yearly[["Year", "rate"]].copy()
    year_overview.columns = ["year", "arrest_rate"]

    monthly_counts = (
        df.groupby("Month")
        .size()
        .reset_index(name="crime_count")
    )
    peak_month = monthly_counts.loc[monthly_counts["crime_count"].idxmax()]

    top_community_counts = (
        df[df["community_area"] != "Unknown"]["community_area"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_community_counts.columns = ["community_area", "count"]

    crime_arrests = (
        df.groupby("primary_type")["arrest"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    crime_arrests.columns = ["crime_category", "arrests"]

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]
    heatmap = (
        df.pivot_table(
            index="Month",
            columns="DayOfWeek",
            values="primary_type",
            aggfunc="size",
            fill_value=0
        )
        .reindex(index=range(1, 13), columns=day_order, fill_value=0)
    )

    most_frequent_category = (
        top_categories.iloc[0]["crime_category"]
        if not top_categories.empty else "Unknown"
    )
    most_frequent_count = int(
        top_categories.iloc[0]["count"]
        if not top_categories.empty else 0
    )
    most_frequent_percentage = (
        top_categories.iloc[0]["percentage"]
        if not top_categories.empty else 0
    )

    print("\nQ1. What percentage of crimes result in arrest?")
    print(f"A1. {arrest_rate:.2f}%.")

    print("\nQ2. Which crime category is most frequent?")
    print(f"A2. {most_frequent_category} ({most_frequent_count} incidents, {most_frequent_percentage:.2f}%).")

    print("\nQ3. Is the arrest rate consistent across different years?")
    print(f"A3. No. The yearly arrest rate ranges from {yearly['rate'].min():.2f}% to {yearly['rate'].max():.2f}%, peaking in {highest_year} at {highest_rate:.2f}%.")

    print("\nQ4. Which month has the highest crime frequency?")
    print(f"A4. Month {int(peak_month['Month'])} with {peak_month['crime_count']} crimes.")
    print("\nTop 10 crime categories and percentages:")
    print(
        top_categories[["crime_category", "count", "percentage"]]
        .head(10)
        .to_string(index=False, formatters={"percentage": "{:.2f}%".format})
    )

    result = {
        "status": "success",

        "kpis": {
            "total_arrests": arrests,
            "arrest_rate": round(arrest_rate, 2),
            "highest_arrest_year": highest_year,
            "highest_arrest_rate": round(highest_rate, 2),
            "most_frequent_crime": most_frequent_category,
            "highest_crime_month": int(peak_month["Month"]),
            "highest_crime_month_count": int(peak_month["crime_count"])
        },

        "crime_trend_over_years": {
            "labels": yearly_counts["Year"].astype(str).tolist(),
            "values": yearly_counts["crime_count"].astype(int).tolist()
        },

        "crime_distribution_by_category": {
            "labels": top_categories["crime_category"].tolist(),
            "values": top_categories["count"].astype(int).tolist(),
            "percentages": top_categories["percentage"].tolist(),
            "table": [
                {
                    "crime_category": row["crime_category"],
                    "count": int(row["count"]),
                    "percentage": float(row["percentage"])
                }
                for _, row in top_categories.iterrows()
            ]
        },

        "arrests_and_crime_outcomes": {
            "labels": ["Arrest", "No Arrest"],
            "values": [arrests, total - arrests],
            "arrest_rate": round(arrest_rate, 2)
        },

        "heatmap_of_crime_by_month_and_day_of_week": {
            "months": list(range(1, 13)),
            "days": day_order,
            "matrix": heatmap.values.tolist()
        },

        "top_community_areas": {
            "labels": top_community_counts["community_area"].tolist(),
            "values": top_community_counts["count"].astype(int).tolist()
        },

        "outcome": {
            "labels": ["Arrest", "No Arrest"],
            "values": [arrests, total - arrests]
        },

        "yearly": {
            "labels": year_overview["year"].astype(str).tolist(),
            "values": year_overview["arrest_rate"].tolist()
        },

        "arrests_by_crime": {
            "labels": crime_arrests["crime_category"].tolist(),
            "values": crime_arrests["arrests"].astype(int).tolist()
        }
    }

    result["summary"] = (
        "Use Case 2 explores crime volume, category dominance, arrest outcomes, and temporal patterns. "
        f"The most frequent crime category is {most_frequent_category} with {most_frequent_count} incidents ({most_frequent_percentage:.2f}% of all crimes). "
        f"The overall arrest rate is {arrest_rate:.2f}%, and the yearly arrest rate varies from {yearly['rate'].min():.2f}% to {yearly['rate'].max():.2f}% across the dataset. "
        f"The highest crime month is month {int(peak_month['Month'])}, when {peak_month['crime_count']} crimes were recorded."
    )

    result["questions_answered"] = [
        f"What percentage of crimes result in arrest? Answer: {arrest_rate:.2f}%.",
        f"Which crime category is most frequent? Answer: {most_frequent_category} ({most_frequent_count} incidents, {most_frequent_percentage:.2f}%).",
        f"Is the arrest rate consistent across different years? Answer: No. The yearly arrest rate ranges from {yearly['rate'].min():.2f}% to {yearly['rate'].max():.2f}% with the peak in {highest_year} ({highest_rate:.2f}%).",
        f"Which month has the highest crime frequency? Answer: Month {int(peak_month['Month'])} with {peak_month['crime_count']} crimes."
    ]

    return result


# =========================================================
# CASE 3
# =========================================================

def case3_time_analysis():

    df = clean_dataframe(load_data())

    print("\n=== Use Case 3: Time, outlier, and correlation analysis ===")
    hourly = df.groupby("Hour").size().reindex(range(24), fill_value=0)
    print("Crimes by hour of day:")
    print(hourly.to_string())

    community_counts = df[df["community_area"] != "Unknown"]["community_area"].value_counts()
    print("\nCommunity crime counts (sample):")
    print(community_counts.head(10).to_string())

    # -----------------------------------------
    # Hour
    # -----------------------------------------

    hourly = (
        df.groupby("Hour")
        .size()
        .reindex(
            range(24),
            fill_value=0
        )
    )

    # -----------------------------------------
    # Month
    # -----------------------------------------

    monthly = (
        df.groupby("Month")
        .size()
        .reindex(
            range(1, 13),
            fill_value=0
        )
    )

    # -----------------------------------------
    # Day
    # -----------------------------------------

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    daily = (
        df.groupby("DayOfWeek")
        .size()
        .reindex(
            day_order,
            fill_value=0
        )
    )

    # -----------------------------------------
    # Heatmap Month x Day
    # -----------------------------------------

    heatmap = (
        df.pivot_table(
            index="Month",
            columns="DayOfWeek",
            values="arrest",
            aggfunc="size",
            fill_value=0
        )
        .reindex(
            index=range(1, 13),
            fill_value=0
        )
        .reindex(
            columns=day_order,
            fill_value=0
        )
    )

    # -----------------------------------------
    # Correlation
    # -----------------------------------------

    numeric = df.select_dtypes(include=np.number)

    correlation = (
        numeric.corr()
        .round(3)
        .replace(
            [np.nan, np.inf, -np.inf],
            0
        )
    )

    # -----------------------------------------
    # Community IQR
    # -----------------------------------------

    community_counts = (
        df[
            df["community_area"] != "Unknown"
        ]
        ["community_area"]
        .value_counts()
    )

    if len(community_counts):

        q1 = float(
            community_counts.quantile(
                0.25
            )
        )

        q3 = float(
            community_counts.quantile(
                0.75
            )
        )

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = community_counts[
            (community_counts > upper) | (community_counts < lower)
        ]

    else:

        q1 = q3 = iqr = lower = upper = 0

        outliers = pd.Series(
            dtype=int
        )

    result = {
        "status": "success",

        "hourly": {
            "labels": [
                str(x)
                for x in range(24)
            ],
            "values": [
                int(x)
                for x in hourly.values
            ]
        },

        "monthly": {
            "labels": [
                str(x)
                for x in range(1, 13)
            ],
            "values": [
                int(x)
                for x in monthly.values
            ]
        },

        "daily": {
            "labels": day_order,
            "values": [
                int(x)
                for x in daily.values
            ]
        },

        "heatmap": {
            "x": day_order,
            "y": [
                str(x)
                for x in range(1, 13)
            ],
            "values": [
                [
                    int(v)
                    for v in heatmap.iloc[i].values
                ]
                for i in range(len(heatmap))
            ]
        },

        "correlation": {
            "labels": correlation.columns.tolist(),
            "values": correlation.values.tolist()
        },

        "outliers": {
            "q1": round(q1, 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
            "lower_bound": round(lower, 2),
            "upper_bound": round(
                upper,
                2
            ),
            "labels": outliers.index.tolist(),
            "values": [
                int(x)
                for x in outliers.values
            ]
        }
    }

    # NumPy descriptive statistics for the community-area crime-count
    # distribution.  IQR thresholds above use this same distribution.
    result["community_clusters"] = {
        "mean_crime_count": round(float(np.mean(community_counts.values)), 2) if len(community_counts) else 0,
        "median_crime_count": round(float(np.median(community_counts.values)), 2) if len(community_counts) else 0,
        "community_areas_analyzed": int(len(community_counts))
    }

    peak_hour = int(hourly.idxmax())
    peak_hour_count = int(hourly.max())
    outlier_labels = result["outliers"]["labels"]

    result["summary"] = (
        "Use Case 3 looks at when crimes are most likely to occur, which areas form statistical outliers, and how the numeric variables relate to one another. "
        f"The busiest hour is {peak_hour}:00, with {peak_hour_count} crimes reported. "
        f"The community-area outlier list identifies {outlier_labels if outlier_labels else 'no major outlier'} as unusually high-risk locations."
    )

    print("\nQ1. What time of day has the highest crime intensity?")
    print(f"A1. {peak_hour}:00 with {peak_hour_count} crimes.")

    print("\nQ2. Which community areas are statistical outliers?")
    print(f"A2. {outlier_labels if outlier_labels else 'No major outliers.'}")

    print("\nQ3. How do numeric crime variables correlate with each other?")
    print("A3. Correlation matrix shows the strongest relationships between the numeric crime fields.")

    result["questions_answered"] = [
        f"What time of day has the highest crime intensity? Answer: {peak_hour}:00 with {peak_hour_count} crimes.",
        f"Which community areas are statistical outliers? Answer: {', '.join(outlier_labels) if outlier_labels else 'No major outliers'}.",
        "How do numeric crime variables correlate with each other? Answer: the correlation matrix displays the relationships among Year, Month, Hour, arrest, and domestic fields.",
        f"What is the mean crime count per community area? Answer: {result['community_clusters']['mean_crime_count']:.2f}."
    ]

    return result


# =========================================================
# CASE 4
# =========================================================

def case4_geographic_analysis():

    df = clean_dataframe(load_data())

    print("\n=== Use Case 4: MySQL reporting and geographic analysis ===")
    yearly = df.groupby("Year").size().reset_index(name="crime_count")
    print("Crime count per year:")
    print(yearly.to_string(index=False))

    top10 = df["primary_type"].value_counts().head(10)
    print("\nTop 10 crime types and percentages:")
    print((top10 / top10.sum() * 100).round(2).to_string())

    # -----------------------------------------
    # Community
    # -----------------------------------------

    communities = (
        df[
            df["community_area"] != "Unknown"
        ]
        ["community_area"]
        .value_counts()
        .head(10)
    )

    community_counts = (
        df[
            df["community_area"] != "Unknown"
        ]
        ["community_area"]
        .value_counts()
    )

    hourly_counts = (
        df.groupby("Hour")
        .size()
        .reindex(
            range(24),
            fill_value=0
        )
    )

    # -----------------------------------------
    # IUCR
    # -----------------------------------------

    iucr = (
        df[
            df["iucr"] != "Unknown"
        ]
        ["iucr"]
        .value_counts()
        .head(10)
    )

    # -----------------------------------------
    # District
    # -----------------------------------------

    districts = (
        df[
            df["district"] != "Unknown"
        ]
        ["district"]
        .value_counts()
        .head(10)
    )

    # -----------------------------------------
    # Heatmap values
    # -----------------------------------------

    heat_values = communities.values.tolist()

    if heat_values:

        max_value = max(
            heat_values
        )

        intensity = [
            round(
                value / max_value * 100,
                2
            )
            for value in heat_values
        ]

    else:

        intensity = []

    # -----------------------------------------
    # IQR outliers
    # -----------------------------------------

    all_community_counts = (
        df[
            df["community_area"] != "Unknown"
        ]
        ["community_area"]
        .value_counts()
    )

    if len(all_community_counts):

        q1 = all_community_counts.quantile(
            0.25
        )

        q3 = all_community_counts.quantile(
            0.75
        )

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = all_community_counts[
            (all_community_counts > upper) | (all_community_counts < lower)
        ]

    else:

        q1 = q3 = iqr = lower = upper = 0

        outliers = pd.Series(
            dtype=int
        )

    community_mean = float(
        np.mean(
            community_counts.values
        )
    ) if len(community_counts) else 0.0

    community_median = float(
        np.median(
            community_counts.values
        )
    ) if len(community_counts) else 0.0

    community_std = float(
        np.std(
            community_counts.values
        )
    ) if len(community_counts) else 0.0

    numeric_columns = [
        col for col in [
            "Year",
            "Month",
            "arrest",
            "domestic"
        ] if col in df.columns
    ]

    correlation = (
        df[numeric_columns]
        .corr()
        .round(3)
        .replace(
            [np.nan, np.inf, -np.inf],
            0
        )
    ) if numeric_columns else pd.DataFrame()

    peak_hour = int(
        hourly_counts.idxmax()
    ) if len(hourly_counts) else None
    peak_hour_count = int(
        hourly_counts.max()
    ) if len(hourly_counts) else 0

    # -----------------------------------------
    # Geographic KPI
    # -----------------------------------------

    highest_area = (
        communities.index[0]
        if len(communities)
        else "No data"
    )

    top_iucr = (
        iucr.index[0]
        if len(iucr)
        else "No data"
    )

    result = {
        "status": "success",

        "kpis": {
            "highest_community": str(
                highest_area
            ),
            "top_iucr": str(
                top_iucr
            ),
            "community_count": int(
                all_community_counts.size
            )
        },

        "hotspots": {
            "labels": communities.index.tolist(),
            "values": [
                int(x)
                for x in communities.values
            ]
        },

        "iucr": {
            "labels": iucr.index.tolist(),
            "values": [
                int(x)
                for x in iucr.values
            ]
        },

        "community": {
            "labels": communities.index.tolist(),
            "values": [
                int(x)
                for x in communities.values
            ]
        },

        "district": {
            "labels": districts.index.tolist(),
            "values": [
                int(x)
                for x in districts.values
            ]
        },

        "crime_by_hour": {
            "labels": [
                str(hour)
                for hour in hourly_counts.index.tolist()
            ],
            "values": [
                int(value)
                for value in hourly_counts.values.tolist()
            ]
        },

        "community_clusters": {
            "mean_crime_count": round(
                community_mean,
                2
            ),
            "median_crime_count": round(
                community_median,
                2
            ),
            "std_dev": round(
                community_std,
                2
            ),
            "q1": round(float(q1), 2),
            "q3": round(float(q3), 2),
            "iqr": round(float(iqr), 2),
            "lower_bound": round(float(lower), 2),
            "upper_bound": round(
                float(upper),
                2
            ),
            "outlier_labels": outliers.index.tolist(),
            "outlier_values": [
                int(x)
                for x in outliers.values
            ]
        },

        "correlation": {
            "columns": list(
                correlation.columns
            ),
            "values": correlation.values.tolist()
        },

        "peak_hour": {
            "hour": peak_hour,
            "count": peak_hour_count
        },

        "heatmap": {
            "labels": communities.index.tolist(),
            "values": [
                int(x)
                for x in communities.values
            ],
            "intensity": intensity
        },

        "outliers": {
            "q1": round(float(q1), 2),
            "q3": round(float(q3), 2),
            "iqr": round(float(iqr), 2),
            "lower_bound": round(float(lower), 2),
            "upper_bound": round(
                float(upper),
                2
            ),
            "labels": outliers.index.tolist(),
            "values": [
                int(x)
                for x in outliers.values
            ]
        }
    }

    # Use Case 4 reporting payload.  The same cleaned table is populated by
    # Python's database connector; SQLite is the documented local fallback
    # when a MySQL server is not configured.
    top10_report = (top10 / len(df) * 100).round(2)
    arrest_by_year = (
        df.groupby("Year")["arrest"].sum().reset_index(name="arrest_count")
    )
    result["sql_reports"] = {
        "crime_count_per_year": [
            {"year": int(row["Year"]), "crime_count": int(row["crime_count"])}
            for _, row in yearly.iterrows()
        ],
        "top10_crime_types": [
            {"crime_type": str(crime), "percentage": float(top10_report[crime])}
            for crime in top10.index
        ],
        "arrest_count_per_year": [
            {"year": int(row["Year"]), "arrest_count": int(row["arrest_count"])}
            for _, row in arrest_by_year.iterrows()
        ],
        "views": ["vw_crime_yearly", "vw_crime_by_category"]
    }

    outlier_label = (
        ", ".join(result["outliers"]["labels"][:5])
        if result["outliers"]["labels"]
        else "no significant outlier"
    )

    peak_hour_label = (
        f"{peak_hour:02d}:00"
        if peak_hour is not None else "N/A"
    )

    result["summary"] = (
        "Use Case 4 identifies the geographic hotspots, dominant crime clusters, and community-level patterns in Chicago. "
        f"The most affected community is {highest_area}, while the most common IUCR code is {top_iucr}. "
        f"The peak crime hour is {peak_hour_label} with {peak_hour_count} recorded incidents. "
        f"The mean community crime count is {community_mean:.2f}, and {outlier_label} are flagged as unusually high-risk community areas compared with the wider distribution."
    )

    result["questions_answered"] = [
        "What is the crime count per year?",
        "What are the top five crime types and their percentages?",
        "What is the arrest count per year?",
        "Which communities should be prioritized for patrol or intervention?"
    ]

    return result
