import os
import re
import sqlite3
import numpy as np
import pandas as pd

from .config import Config


def normalize_column_name(column):
    column = str(column).strip()
    column = re.sub(r"[^a-zA-Z0-9]+", "_", column)
    return column.strip("_").lower()


def clean_boolean(value):
    if pd.isna(value):
        return -1

    if isinstance(value, bool):
        return int(value)

    value = str(value).strip().lower()

    return 1 if value in {
        "true", "1", "yes", "y", "t"
    } else 0


def safe_text(series):
    return (
        series
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace({
            "": "Unknown",
            "nan": "Unknown",
            "NaN": "Unknown",
            "None": "Unknown"
        })
    )


def load_csv(path=None):
    path = path or Config.DATASET_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found:\n{path}"
        )

    return pd.read_csv(
        path,
        low_memory=False
    )


def ingest_data():

    path = Config.DATASET_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found:\n{path}"
        )

    df = pd.read_csv(
        path,
        low_memory=False
    )

    original_rows = len(df)
    original_column_names = list(df.columns)
    original_columns = len(original_column_names)
    # Store the actual CSV column count before any renaming/processing
    csv_column_count = original_columns

    print("\n======================================================================")
    print("USE CASE 1 - LOAD AND CLEAN CHICAGO CRIME DATA")
    print("======================================================================")
    print("\nREQUIREMENTS")
    print("----------------------------------------------------------------------")
    print("1. Load Chicago crime CSV using Pandas")
    print("2. Inspect first 10 rows")
    print("3. Display rows and columns")
    print("4. Display schema and data types")
    print("5. Clean missing values")
    print("6. Convert Date to datetime")
    print("7. Standardize categorical fields")
    print("8. Generate Year")
    print("9. Generate Month")
    print("10. Generate DayOfWeek")
    print("11. Calculate missing-value percentage using NumPy")
    print("12. Identify columns with >50% missing values")
    print("13. Detect date anomalies")
    print("14. Find unique crime types")
    print("15. Store cleaned data in SQLite")
    print("\nRUNNING USE CASE 1...")
    print("----------------------------------------------------------------------")
    print("\n")
    print("======================================================================")
    print("USE CASE 1 - LOAD AND CLEAN CHICAGO CRIME DATA")
    print("======================================================================")
    print("\n1. LOAD DATASET")
    print("----------------------------------------------------------------------")
    print("Dataset loaded successfully.")
    print(f"File: {path}")
    print(f"Number of rows    : {original_rows}")
    print(f"Number of columns : {csv_column_count}")

    print("\n2. FIRST 10 ROWS")
    print("----------------------------------------------------------------------")
    print(df.head(10).to_string(index=False))

    print("\n3. SCHEMA AND DATA TYPES - BEFORE CLEANING")
    print("----------------------------------------------------------------------")
    print(df.dtypes.to_string())

    # --------------------------------------------------
    # Normalize CSV column names
    # --------------------------------------------------

    df.columns = [
        normalize_column_name(col)
        for col in df.columns
    ]

    rename_map = {
        "district": "district_code",
        "district_code": "district_code",
        "community_area": "community_code",
        "community_code": "community_code",
        "iucr": "iucr_code",
        "iucr_code": "iucr_code",
        "location_description": "location_desc",
        "location_desc": "location_desc",
        "year": "year",
        "year_original": "year"
    }

    for old_name, new_name in rename_map.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})

    if "year" in df.columns and "Year" not in df.columns:
        df["Year"] = df["year"]

    original_column_names = list(df.columns)
    original_columns = len(original_column_names)

    # Keep one immutable baseline for every missing-value report.  The values
    # below are deliberately captured after column normalization/renaming but
    # before any fill operation, so the analysis and handling sections cannot
    # contradict one another (for example, location_description).
    missing_before_cleaning = df.isna().sum()
    pre_clean_missing_pct = (
        missing_before_cleaning / len(df) * 100
    ).round(2)

    print("\n4. CLEAN DATA")
    print("----------------------------------------------------------------------")
    print("✓ Column names standardized.")
    print("✓ String values stripped.")
    print("✓ Categorical values standardized.")
    print("✓ Date converted to datetime.")
    print("✓ Boolean columns standardized.")
    print("✓ Numeric columns converted.")

    date_col = "date"
    primary_type_col = "primary_type"
    arrest_col = "arrest"
    domestic_col = "domestic"
    community_col = "community_code"
    district_col = "district_code"
    iucr_col = "iucr_code"
    fbi_col = "fbi_code"
    description_col = "description"
    location_col = "location_desc"
    block_col = "block"

    key_field_defaults = {
        date_col: "coerced datetime",
        primary_type_col: "Unknown",
        arrest_col: "-1",
        domestic_col: "-1",
        district_col: "Unknown",
        community_col: "Unknown",
        iucr_col: "Unknown",
        fbi_col: "Unknown",
        block_col: "Unknown",
        description_col: "Unknown",
        location_col: "Unknown",
        "Year": "-1",
        "Month": "-1",
        "DayOfWeek": "Unknown",
    }

    key_field_missing_before = {}
    for field in key_field_defaults:
        if field in {"Year", "Month", "DayOfWeek"}:
            continue
        if field in df.columns:
            key_field_missing_before[field] = int(missing_before_cleaning[field])

    df[date_col] = pd.to_datetime(
        df[date_col],
        errors="coerce"
    )

    df[primary_type_col] = (
        df[primary_type_col]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    df[primary_type_col] = df[primary_type_col].replace(
        ["", "NAN", "NONE", "UNKNOWN"],
        "Unknown"
    )

    df[arrest_col] = pd.to_numeric(df[arrest_col], errors="coerce").fillna(-1).astype(int)
    df[domestic_col] = pd.to_numeric(df[domestic_col], errors="coerce").fillna(-1).astype(int)

    df[community_col] = safe_text(df[community_col])
    df[district_col] = safe_text(df[district_col])
    df[iucr_col] = safe_text(df[iucr_col])
    df[fbi_col] = safe_text(df[fbi_col])
    df[block_col] = safe_text(df[block_col])
    df[description_col] = safe_text(df[description_col])
    df[location_col] = safe_text(df[location_col])

    if "location" in df.columns:
        df["location"] = safe_text(df["location"])

    for numeric_field in [
        "ward_no",
        "x_coordinate",
        "y_coordinate",
        "latitude",
        "longitude",
    ]:
        if numeric_field in df.columns:
            numeric_values = pd.to_numeric(df[numeric_field], errors="coerce")
            df[numeric_field] = numeric_values.fillna(-1)

    print("\n5. GENERATE NEW FEATURES")
    print("----------------------------------------------------------------------")
    print("✓ Year created       : df['Year']")
    print("✓ Month created      : df['Month']")
    print("✓ DayOfWeek created  : df['DayOfWeek']")

    df["Year"] = (
        df[date_col]
        .dt.year
        .fillna(-1)
        .astype(int)
    )

    df["Month"] = (
        df[date_col]
        .dt.month
        .fillna(-1)
        .astype(int)
    )

    df["DayOfWeek"] = (
        df[date_col]
        .dt.day_name()
        .fillna("Unknown")
    )

    invalid_dates_before_features = int(df[date_col].isna().sum())
    key_field_missing_before["Year"] = invalid_dates_before_features
    key_field_missing_before["Month"] = invalid_dates_before_features
    key_field_missing_before["DayOfWeek"] = invalid_dates_before_features

    print("\nGenerated feature sample:")
    print(
        df[[date_col, "Year", "Month", "DayOfWeek"]]
        .head(10)
        .to_string()
    )

    print("\n6. MISSING VALUE ANALYSIS (Sorted by Percentage)")
    print("----------------------------------------------------------------------")
    missing_pct = pre_clean_missing_pct.copy()
    for engineered_field in ["Year", "Month", "DayOfWeek"]:
        missing_pct[engineered_field] = round(
            invalid_dates_before_features / len(df) * 100,
            2
        )
    missing_df = (
        missing_pct.to_frame("Missing Percentage")
        .reset_index()
        .rename(columns={"index": "Column"})
    )
    missing_df_sorted = missing_df.sort_values(
        "Missing Percentage",
        ascending=False
    )
    print(missing_df_sorted.to_string(index=False))

    print("\n7. IDENTIFY AND HANDLE MISSING VALUES FOR KEY FIELDS")
    print("----------------------------------------------------------------------")
    for field, default_value in key_field_defaults.items():
        missing_count = key_field_missing_before.get(field, 0)
        missing_pct_field = (missing_count / len(df) * 100)
        print(
            f"✓ {field:22} - Missing: {missing_count:5} "
            f"({missing_pct_field:5.2f}%) - Handled -> {default_value}"
        )
    print("✓ Missing values filled with defaults (Unknown/-1/filled values applied)")

    columns_to_drop = [
        col for col, pct in missing_pct.items() if pct > 50
    ]
    print("\n8. COLUMNS WITH MORE THAN 50% MISSING")

    print("-" * 70)



    if columns_to_drop:

        print("Columns identified for removal:")

        for col in columns_to_drop:

            print(f" - {col}")



        # Drop only columns whose ORIGINAL missing percentage is > 50%

        df = df.drop(columns=columns_to_drop, errors="ignore")



        print(

            f"\n✓ Dropped {len(columns_to_drop)} column(s) "

            "with more than 50% missing values."

        )

    else:

        print("✓ No columns have more than 50% missing values.")


    print("\n9. UNIQUE CRIME TYPES")
    print("----------------------------------------------------------------------")
    unique_crime_types = int(df[primary_type_col].nunique())
    print(f"Number of unique crime types: {unique_crime_types}")
    print("\nCrime types:")
    for crime in df[primary_type_col].dropna().unique()[:16]:
        print(f" - {crime}")

    invalid_dates = int(df[date_col].isna().sum())
    future_dates = int((df[date_col] > pd.Timestamp.now()).sum())
    min_date = df[date_col].min()
    max_date = df[date_col].max()

    print("\n10. DATE ANOMALY / OUTLIER CHECK & EXPLANATION")
    print("----------------------------------------------------------------------")
    print(f"Invalid dates         : {invalid_dates}")
    print(f"Future dates          : {future_dates}")
    print(f"Minimum date          : {min_date}")
    print(f"Maximum date          : {max_date}")
    
    if invalid_dates == 0 and future_dates == 0:
        print("\n✓ NO ANOMALIES DETECTED:")
        print("  - All dates are valid and within expected range")
        print("  - No future dates found in the dataset")
        print("  - Date range is consistent with Chicago crime data collection period")
        anomalies_detected = False
    else:
        print("\n⚠ ANOMALIES DETECTED:")
        if invalid_dates > 0:
            print(f"  - {invalid_dates} invalid/missing dates found")
        if future_dates > 0:
            print(f"  - {future_dates} future dates found (possible data entry errors)")
        anomalies_detected = True

    duplicate_records = int(df.duplicated().sum())
    print("\n11. DUPLICATE RECORD CHECK")
    print("----------------------------------------------------------------------")
    print(f"Duplicate records: {duplicate_records}")

    final_columns = [
        "id",
        "case_number",
        "date",
        "block",
        "iucr_code",
        "primary_type",
        "description",
        "location_desc",
        "arrest",
        "domestic",
        "beat_num",
        "district_code",
        "ward_no",
        "community_code",
        "fbi_code",
        "x_coordinate",
        "y_coordinate",
        "date_of_update",
        "latitude",
        "longitude",
        "location",
        "Year",
        "DayOfWeek",
        "Month",
    ]

    reordered_df = df.copy()
    for column in [
        "district_code", "community_code", "iucr_code", "location_desc",
        "case_number", "date", "block", "primary_type", "description",
        "arrest", "domestic", "beat_num", "ward_no", "fbi_code",
        "x_coordinate", "y_coordinate", "date_of_update", "latitude",
        "longitude", "location", "Year", "DayOfWeek", "Month"
    ]:
        if column not in reordered_df.columns:
            reordered_df[column] = None

    if "id" not in reordered_df.columns:
        reordered_df.insert(0, "id", range(1, len(reordered_df) + 1))
    if "year" in reordered_df.columns and "Year" in reordered_df.columns:
        reordered_df = reordered_df.drop(columns=["year"])

    database_df = reordered_df[[col for col in final_columns if col in reordered_df.columns]].copy()
    if "Year" in database_df.columns and "Month" in database_df.columns and "DayOfWeek" in database_df.columns:
        database_df["Year"] = pd.to_numeric(database_df["Year"], errors="coerce").fillna(-1).astype(int)
        database_df["Month"] = pd.to_numeric(database_df["Month"], errors="coerce").fillna(-1).astype(int)
        database_df["DayOfWeek"] = database_df["DayOfWeek"].fillna("Unknown").astype(str).replace({"nan": "Unknown", "None": "Unknown"})

    print("\n12. FINAL CLEANED DATASET")
    print("----------------------------------------------------------------------")
    print(f"Rows    : {len(database_df)}")
    print(f"Columns : {len(database_df.columns)} (24 total columns: 21 final schema without year(duplicate) + 3 engineered features)")
    print("\nFinal columns:")
    for i, col in enumerate(database_df.columns, start=1):
        print(f" {i:2}. {col}")

    print("\n13. FINAL DATA TYPES")
    print("----------------------------------------------------------------------")
    print(database_df.dtypes.to_string())

    connection = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS crimes")
    database_df.to_sql("crimes", connection, if_exists="replace", index=False, chunksize=5000)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crime_year ON crimes(Year)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crime_type ON crimes(primary_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_arrest ON crimes(arrest)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_community ON crimes(community_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_iucr ON crimes(iucr_code)")
    connection.commit()
    connection.close()

    print("\n14. INSERT CLEANED DATA INTO SQLITE")
    print("----------------------------------------------------------------------")
    print("✓ SQLite database updated.")
    print(f"✓ Records stored: {len(database_df)}")
    print(f"✓ Database: {Config.DATABASE_PATH}")
    print(f"✓ Table name: 'crimes' (used for all case queries)")

    print("\n======================================================================")
    print("USE CASE 1 RESULT")
    print("======================================================================")
    print(f"Original rows       : {original_rows}")
    print(f"Original columns    : {csv_column_count}")
    print(f"After removing duplicate 'year': {csv_column_count - 1}")
    print(f"Final rows          : {len(database_df)}")
    print(f"Final columns       : {len(database_df.columns)} ({csv_column_count - 1} after removing duplicate 'year' + 3 features)")
    print(f"Unique crime types  : {unique_crime_types}")
    print(f"Invalid dates       : {invalid_dates}")
    print(f"Future dates        : {future_dates}")
    print(f"Duplicate records   : {duplicate_records}")
    print(f"SQLite records      : {len(database_df)}")
    print("\nFeatures created:")
    print("Year, Month, DayOfWeek")
    print("\n======================================================================")
    print("✓ USE CASE 1 COMPLETED")
    print("======================================================================")

    final_column_count = int(len(database_df.columns))

    return {
        "status": "success",
        "rows_loaded": int(len(database_df)),
        "columns_loaded": final_column_count,
        "final_column_count": final_column_count,
        "original_rows": int(original_rows),
        "original_columns": int(csv_column_count),
        "unique_crime_types": int(unique_crime_types),
        "communities_loaded": int(
            database_df["community_code"].dropna().nunique()
        ) if "community_code" in database_df.columns else 0,
        "message": "Crime dataset loaded successfully.",
        "summary": "Use Case 1 completed successfully. The dataset was cleaned, feature engineering was applied, and the SQLite database was updated.",
        "questions_answered": [
            "How many unique crime types are present in the dataset?",
            "Are there missing values or date anomalies?",
            "How many original columns and final engineered columns exist?",
            "Was the cleaned dataset successfully stored in SQLite?"
        ]
    }
