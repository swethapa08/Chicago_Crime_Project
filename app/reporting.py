import os
import pandas as pd

from .config import Config
from .database import get_connection
from .analysis import (
    crime_summary,
    yearly_trend,
    top_communities,
    crime_by_district
)


def ensure_report_directory():
    os.makedirs(
        Config.REPORTS_DIR,
        exist_ok=True
    )


def generate_report_files():
    conn = get_connection()

    try:
        df = pd.read_sql(
            "SELECT * FROM crimes",
            conn
        )
    finally:
        conn.close()

    if df.empty:
        return {}

    ensure_report_directory()

    df = df.copy()
    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    ).fillna(0).astype(int)

    df["Month"] = pd.to_numeric(
        df["Month"],
        errors="coerce"
    ).fillna(0).astype(int)

    if "date" in df.columns:
        df["Hour"] = pd.to_datetime(df["date"], errors="coerce").dt.hour.fillna(-1).astype(int)
    elif "Hour" in df.columns:
        df["Hour"] = pd.to_numeric(
            df["Hour"],
            errors="coerce"
        ).fillna(-1).astype(int)
    else:
        df["Hour"] = 0

    df["arrest"] = pd.to_numeric(
        df["arrest"],
        errors="coerce"
    ).fillna(0).astype(int)

    yearly = (
        df.groupby("Year")
        .agg(
            crime_count=("Year", "size"),
            arrest_count=("arrest", "sum")
        )
        .reset_index()
    )
    yearly["arrest_rate"] = (
        yearly["arrest_count"] / yearly["crime_count"] * 100
    ).round(2)
    yearly.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "crime_count_per_year.csv"
        ),
        index=False
    )

    arrest_year = yearly[["Year", "arrest_count"]].copy()
    arrest_year.columns = ["year", "arrest_count"]
    arrest_year.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "arrest_count_per_year.csv"
        ),
        index=False
    )

    top10 = (
        df["primary_type"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top10.columns = ["primary_type", "crime_count"]
    top10["percentage"] = (
        top10["crime_count"] / top10["crime_count"].sum() * 100
    ).round(2)
    top10.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "top10_crime_types.csv"
        ),
        index=False
    )

    iucr = (
        df[["iucr_code", "primary_type", "description"]]
        .fillna("Unknown")
        .copy()
    )
    top_iucr = (
        iucr.groupby(["iucr_code", "primary_type", "description"])
        .size()
        .reset_index(name="crime_count")
        .sort_values("crime_count", ascending=False)
        .head(10)
        .rename(columns={"iucr_code": "iucr_code"})
    )
    top_iucr.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "top10_iucr_codes.csv"
        ),
        index=False
    )

    missing = pd.DataFrame({
        "column": df.columns,
        "missing_count": df.isna().sum().values,
        "missing_percentage": (df.isna().mean() * 100).round(2).values
    })
    missing.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "missing_values.csv"
        ),
        index=False
    )

    crime_by_hour = (
        df["Hour"].value_counts().sort_index().reset_index()
    ) if "Hour" in df.columns else pd.DataFrame({"hour": [], "crime_count": []})
    if not crime_by_hour.empty:
        crime_by_hour.columns = ["hour", "crime_count"]
    crime_by_hour.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "crime_by_hour.csv"
        ),
        index=False
    )

    monthly_crime_frequency = (
        df.groupby("Month").size().reindex(range(1, 13), fill_value=0).reset_index()
    )
    monthly_crime_frequency.columns = ["month", "crime_count"]
    monthly_crime_frequency.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "monthly_crime_frequency.csv"
        ),
        index=False
    )

    community_counts = (
        df[df["community_area"] != "Unknown"]["community_area"].value_counts().reset_index()
        if "community_area" in df.columns else pd.DataFrame(columns=["community_area", "crime_count"])
    )
    if not community_counts.empty:
        community_counts.columns = ["community_area", "crime_count"]
    community_counts.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "top10_community_areas.csv"
        ),
        index=False
    )

    community_outliers = pd.DataFrame()
    if "community_area" in df.columns:
        area_counts = df[df["community_area"] != "Unknown"]["community_area"].value_counts()
        if not area_counts.empty:
            q1 = float(area_counts.quantile(0.25))
            q3 = float(area_counts.quantile(0.75))
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = area_counts[(area_counts > upper) | (area_counts < lower)]
            community_outliers = pd.DataFrame({
                "community_area": outliers.index,
                "crime_count": outliers.values,
                "lower_bound": lower,
                "upper_bound": upper,
                "iqr": iqr
            })
    community_outliers.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "community_outlier_summary.csv"
        ),
        index=False
    )

    yearly_arrest_rate = (
        df.groupby("Year").apply(
            lambda g: (g["arrest"].sum() / len(g) * 100) if len(g) else 0
        ).reset_index(name="arrest_rate")
    )
    yearly_arrest_rate.columns = ["year", "arrest_rate"]
    yearly_arrest_rate.to_csv(
        os.path.join(
            Config.REPORTS_DIR,
            "arrest_rate_by_year.csv"
        ),
        index=False
    )

    print("\n=== GENERATED REPORT FILES ===")
    for name in [
        "crime_count_per_year.csv",
        "arrest_count_per_year.csv",
        "top10_crime_types.csv",
        "top10_iucr_codes.csv",
        "missing_values.csv",
        "crime_by_hour.csv",
        "monthly_crime_frequency.csv",
        "top10_community_areas.csv",
        "community_outlier_summary.csv",
        "arrest_rate_by_year.csv"
    ]:
        print(f"- {os.path.join(Config.REPORTS_DIR, name)}")

    return {
        "crime_count_per_year": yearly.to_dict(orient="records"),
        "top10_crime_types": top10.to_dict(orient="records"),
        "top10_iucr_codes": top_iucr.to_dict(orient="records"),
        "missing_values": missing.to_dict(orient="records"),
        "crime_by_hour": crime_by_hour.to_dict(orient="records"),
        "monthly_crime_frequency": monthly_crime_frequency.to_dict(orient="records"),
        "top10_community_areas": community_counts.to_dict(orient="records"),
        "community_outlier_summary": community_outliers.to_dict(orient="records"),
        "arrest_rate_by_year": yearly_arrest_rate.to_dict(orient="records")
    }


def create_reporting_tables():

    conn = get_connection()

    try:

        conn.execute(
            "DROP TABLE IF EXISTS crime_summary"
        )

        conn.execute(
            "DROP TABLE IF EXISTS yearly_crime_summary"
        )

        conn.execute(
            "DROP TABLE IF EXISTS community_crime_summary"
        )

        conn.execute(
            "DROP TABLE IF EXISTS district_crime_summary"
        )

        summary = crime_summary()

        summary_df = pd.DataFrame([
            {
                "metric": "total_crimes",
                "value": summary[
                    "total_crimes"
                ]
            },
            {
                "metric": "unique_crime_types",
                "value": summary[
                    "unique_crime_types"
                ]
            },
            {
                "metric": "arrests",
                "value": summary[
                    "arrests"
                ]
            },
            {
                "metric": "arrest_rate",
                "value": summary[
                    "arrest_rate"
                ]
            }
        ])

        summary_df.to_sql(
            "crime_summary",
            conn,
            if_exists="replace",
            index=False
        )

        yearly_df = pd.DataFrame(
            yearly_trend()
        )

        if not yearly_df.empty:

            yearly_df.to_sql(
                "yearly_crime_summary",
                conn,
                if_exists="replace",
                index=False
            )

        community_df = pd.DataFrame(
            top_communities()
        )

        if not community_df.empty:

            community_df.to_sql(
                "community_crime_summary",
                conn,
                if_exists="replace",
                index=False
            )

        district_df = pd.DataFrame(
            crime_by_district()
        )

        if not district_df.empty:

            district_df.to_sql(
                "district_crime_summary",
                conn,
                if_exists="replace",
                index=False
            )

        create_views(conn)

        conn.commit()

    finally:
        conn.close()


def create_views(conn):

    conn.execute(
        "DROP VIEW IF EXISTS vw_crime_overview"
    )

    conn.execute(
        "DROP VIEW IF EXISTS vw_top_crimes"
    )

    conn.execute(
        "DROP VIEW IF EXISTS vw_yearly_crime"
    )

    conn.execute(
        "DROP VIEW IF EXISTS vw_crime_yearly"
    )

    conn.execute(
        "DROP VIEW IF EXISTS vw_crime_by_category"
    )

    conn.execute(
        """
        CREATE VIEW vw_crime_overview AS
        SELECT
            metric,
            value
        FROM crime_summary
        """
    )

    conn.execute(
        """
        CREATE VIEW vw_yearly_crime AS
        SELECT
            year,
            count
        FROM yearly_crime_summary
        """
    )

    conn.execute(
        """
        CREATE VIEW vw_crime_yearly AS
        SELECT
            year,
            COUNT(*) AS crime_count
        FROM crimes
        GROUP BY year
        ORDER BY year
        """
    )

    conn.execute(
        """
        CREATE VIEW vw_crime_by_category AS
        SELECT
            primary_type AS crime_type,
            COUNT(*) AS crime_count,
            ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM crimes), 2) AS percentage
        FROM crimes
        WHERE primary_type IS NOT NULL
        GROUP BY primary_type
        ORDER BY crime_count DESC
        LIMIT 5
        """
    )

    conn.execute(
        """
        CREATE VIEW vw_top_crimes AS
        SELECT
            crime,
            count
        FROM (
            SELECT
                primary_type AS crime,
                COUNT(*) AS count
            FROM crimes
            WHERE primary_type IS NOT NULL
            GROUP BY primary_type
            ORDER BY count DESC
            LIMIT 10
        )
        """
    )


def get_reporting_summary():

    conn = get_connection()

    try:

        overview = pd.read_sql_query(
            """
            SELECT *
            FROM vw_crime_overview
            """,
            conn
        )

        yearly = pd.read_sql_query(
            """
            SELECT *
            FROM vw_yearly_crime
            ORDER BY year
            """,
            conn
        )

        top_crimes = pd.read_sql_query(
            """
            SELECT *
            FROM vw_top_crimes
            """,
            conn
        )

        yearly_view = pd.read_sql_query(
            """
            SELECT *
            FROM vw_crime_yearly
            ORDER BY year
            """,
            conn
        )

        category_view = pd.read_sql_query(
            """
            SELECT *
            FROM vw_crime_by_category
            ORDER BY crime_count DESC
            """,
            conn
        )

        return {
            "overview":
                overview.to_dict(
                    orient="records"
                ),

            "yearly":
                yearly.to_dict(
                    orient="records"
                ),

            "top_crimes":
                top_crimes.to_dict(
                    orient="records"
                ),

            "yearly_view":
                yearly_view.to_dict(
                    orient="records"
                ),

            "category_view":
                category_view.to_dict(
                    orient="records"
                )
        }

    finally:
        conn.close()


def run_use_case_4():

    print("\n")
    print("=" * 80)
    print("USE CASE 4 - MYSQL REPORTING & INTEGRATION")
    print("=" * 80)

    if Config.MYSQL_USE:
        print("MySQL mode enabled.")
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()")
            print(f"Connected to MySQL database: {cursor.fetchone()[0]}")
            create_reporting_tables()
        finally:
            conn.close()
    else:
        print("MySQL not configured. Falling back to SQLite for local execution.")
        create_reporting_tables()

    result = get_reporting_summary()

    print("\nSQL REPORTS")
    print("- Crime count per year")
    print(pd.DataFrame(result["yearly_view"]).to_string(index=False))
    print("\n- Top 5 crime types and percentages")
    print(pd.DataFrame(result["category_view"]).to_string(index=False))

    print("\n- Arrest count per year")
    arrest_df = pd.DataFrame(result["yearly"])
    if not arrest_df.empty and "count" in arrest_df.columns:
        arrest_df = arrest_df.rename(columns={"count": "crime_count"})
    print(arrest_df.to_string(index=False))

    return result


if __name__ == "__main__":
    run_use_case_4()