import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


class Config:

    DATASET_PATH = os.path.join(
        BASE_DIR,
        "Chicago_Datasets_Python",
        "chicago_crime_dataset.csv"
    )

    CRIME_CSV = DATASET_PATH

        
    PATROL_REQUESTS_CSV = os.path.join(
        BASE_DIR,
        "Chicago_Datasets_Python",
        "patrol_requests.csv"
    )


    DATABASE_DIR = os.path.join(
        BASE_DIR,
        "database"
    )

    os.makedirs(DATABASE_DIR, exist_ok=True)

    DATABASE_PATH = os.path.join(
        DATABASE_DIR,
        "chicago_crime.db"
    )

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "chicago_crime")
    MYSQL_USE = os.getenv("USE_MYSQL", "false").strip().lower() in {
        "1", "true", "yes", "y"
    }

    REPORTS_DIR = os.path.join(
        BASE_DIR,
        "outputs",
        "reports"
    )

    CHARTS_DIR = os.path.join(
        BASE_DIR,
        "outputs",
        "charts"
    )

    VISUALIZATION_DIR = CHARTS_DIR