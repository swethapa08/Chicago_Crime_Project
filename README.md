# Chicago Crime Analytics Platform

A comprehensive Python/Flask-based analytics platform for analyzing Chicago crime data. This project demonstrates data ingestion, exploratory analysis, statistical pattern detection, and database reporting through four interconnected use cases.

## 📋 Project Overview

This platform provides a complete crime analytics solution with:
- **Data Ingestion & Cleaning** (Use Case 1)
- **Exploratory Analysis & Visualization** (Use Case 2)
- **Statistical Insights & Pattern Detection** (Use Case 3)
- **MySQL Reporting & Integration** (Use Case 4)
- **Patrol Requests CRUD System** (Bonus feature)

---

## 🗂️ Project Structure

```
Chicago_Project/
├── app/
│   ├── __init__.py
│   ├── analysis.py              # USE CASE 2 & Helper Functions
│   ├── statistics.py            # USE CASE 3 - Statistical Analysis
│   ├── reporting.py             # USE CASE 4 - MySQL Reporting
│   ├── visualization.py         # All Use Cases - Chart Creation
│   ├── ingestion.py             # USE CASE 1 - Data Ingestion
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database & Patrol Requests CRUD
│   ├── models.py                # Data models
│   └── routes.py                # Flask API endpoints
├── templates/                   # HTML templates
├── static/                      # CSS, JavaScript files
├── Chicago_Datasets_Python/     # Raw CSV data files
├── outputs/
│   ├── charts/                  # Generated visualization files
│   └── reports/                 # CSV report files
├── database/                    # SQLite database directory
├── app.py                       # Flask application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone and Navigate
```bash
cd Chicago_Project
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

---

## 📊 Use Cases Breakdown

### **USE CASE 1: Data Ingestion & Cleaning**
**File:** `app/ingestion.py`

**Objective:** Load, clean, and transform raw Chicago crime data.

**Tasks:**
- Load crime data from CSV files
- Handle missing values and data type conversions
- Create engineered features (Year, Month, DayOfWeek, Hour)
- Validate data quality and detect anomalies

**API Endpoint:**
```bash
GET /api/ingest
POST /api/ingest
```

**Key Functions:**
- `ingest_data()` - Main ingestion pipeline
- `load_csv()` - Load data from CSV
- Data cleaning and transformation routines

**Output:**
- Cleaned crime data loaded into SQLite database
- Generates summary statistics (total rows, columns, unique crime types)

---

### **USE CASE 2: Exploratory Analysis & Visualization**
**Files:** `app/analysis.py`, `app/visualization.py`

**Objective:** Analyze trends and patterns using Pandas, NumPy, Matplotlib, and Seaborn.

**Tasks:**

1. **Crime Trend Over Years**
   - Plot total number of crimes per year
   - Visual interpretation: Is crime rate rising or decreasing?

2. **Crime Distribution by Category**
   - Bar chart of top 10 crime categories
   - Calculate counts and percentage for each

3. **Arrests and Crime Outcomes**
   - Calculate: `arrest_rate = df['Arrest'].mean() * 100`
   - Pie chart of Arrest vs No Arrest

4. **Heatmap of Crime by Month and Day of Week**
   - Pivot table: Crime frequency by Month vs DayOfWeek
   - Seaborn heatmap visualization

5. **Top Community Areas**
   - List top 10 community areas with highest crime counts
   - Bar chart visualization

**Questions Answered:**
- Which crime category is most frequent?
- Is the arrest rate consistent across different years?
- Which month has the highest crime frequency?
- Which communities have the highest crime volumes?

**API Endpoint:**
```bash
GET /api/analyse?case=2
```

**Key Functions:**
- `case2_arrest_analysis()` - Main analysis function
- `crime_summary()` - Overall crime summary
- `yearly_trend()` - Crime trends by year
- `top_communities()` - Top 10 communities
- Various visualization functions in `visualization.py`

**Generated Charts:**
- `01_crimes_by_year.png` - Crime trend over years
- `02_top10_categories.png` - Crime distribution by category
- `03_arrest_rate_by_year.png` - Yearly arrest rates
- `04_month_day_heatmap.png` - Heatmap by month and day of week
- `05_top10_communities.png` - Top 10 community areas

---

### **USE CASE 3: Statistical Insights & Pattern Detection**
**Files:** `app/statistics.py`, `app/visualization.py`

**Objective:** Use numerical and visual analysis to derive deeper insights.

**Tasks:**

1. **Crime Intensity by Time**
   - Extract hourly distribution: `df['Hour'] = df['Date'].dt.hour`
   - Group by hour: `crimes_by_hour = df.groupby('Hour').size()`
   - Line plot of crimes per hour of day

2. **Community Area Clusters Using NumPy**
   - Compute mean crime per community area
   - Identify statistical outliers using IQR method
   - Box plot visualization with outlier bounds

3. **Crime Cross-Correlation**
   - Correlation matrix: `pd.corr()` on numeric features
   - Visualize correlation with heatmap

**Questions Answered:**
- What time of day has the highest crime intensity?
- Which community areas are statistical outliers?
- How do numeric crime variables correlate with each other?
- What is the mean crime count per community area?

**API Endpoint:**
```bash
GET /api/analyse?case=3
```

**Key Functions:**
- `case3_time_analysis()` - Main analysis function
- `hourly_statistics()` - Crimes by hour
- `peak_hour()` - Peak crime hour
- `community_area_outliers()` - IQR-based outlier detection
- `correlation_matrix()` - Cross-correlation analysis
- `numerical_statistics()` - Descriptive statistics
- `iqr_outliers()` - IQR outlier detection for all numeric columns

**Generated Charts:**
- `06_crimes_by_hour.png` - Hourly crime distribution
- `07_community_boxplot.png` - Community outlier box plot
- `08_correlation_heatmap.png` - Feature correlation matrix

---

### **USE CASE 4: MySQL Reporting & Integration**
**Files:** `app/reporting.py`, `app/visualization.py`

**Objective:** Store, query, and present analytical results from database.

**Tasks:**

1. **Design & Populate Summary Tables**
   - Create SQL tables via Python MySQL Connector
   - Populate with aggregated crime data

2. **MySQL Queries**
   - Crime count per year
   - Top 5 crime types and percentages
   - Arrest count per year

3. **Database Stored Views**
   - `vw_crime_yearly` - Crime count by year
   - `vw_crime_by_category` - Top 5 crime types with percentages
   - `vw_crime_overview` - Overall crime metrics
   - `vw_top_crimes` - Top 10 crime types

4. **Pandas Integration**
   - Read views into DataFrames: `pd.read_sql("SELECT * FROM view_name", conn)`
   - Further analysis and transformation

5. **Visualization from MySQL Data**
   - Plot SQL extracted data with Matplotlib and Seaborn

**Questions Answered:**
- What is the crime count per year?
- What are the top five crime types and their percentages?
- What is the arrest count per year?
- Which communities should be prioritized for intervention?

**API Endpoint:**
```bash
GET /api/analyse?case=4
```

**Key Functions:**
- `case4_geographic_analysis()` - Main analysis function
- `create_reporting_tables()` - Create summary tables
- `create_views()` - Create database views
- `get_reporting_summary()` - Query views and aggregate
- `generate_report_files()` - Export to CSV files

**Generated Reports (CSV):**
- `crime_count_per_year.csv`
- `arrest_count_per_year.csv`
- `top10_crime_types.csv`
- `top10_iucr_codes.csv`
- `top10_community_areas.csv`
- `community_outlier_summary.csv`
- `arrest_rate_by_year.csv`
- `crime_by_hour.csv`
- `monthly_crime_frequency.csv`
- `missing_values.csv`

**Generated Charts:**
- `09_mysql_crimes_by_year.png` - From vw_crime_yearly view
- `10_mysql_top5_crime_types.png` - From vw_crime_by_category view

---

## 🚨 Bonus Feature: Patrol Requests CRUD

**File:** `app/routes.py`, `app/database.py`

A RESTful CRUD system for managing patrol requests.

**API Endpoints:**

```bash
# List all patrol requests
GET /api/patrol-requests

# Create new patrol request
POST /api/patrol-requests
Content-Type: application/json
{
  "ward_no": 1,
  "district_code": 2,
  "community_code": "001",
  "patrol_area": "Downtown",
  "priority": "High",
  "reason": "Traffic Control",
  "requested_by": "Dispatcher",
  "assigned_officers": 2,
  "status": "PENDING",
  "perimeter_radius": 5.5
}

# Get specific patrol request
GET /api/patrol-requests/<request_id>

# Update patrol request
PUT /api/patrol-requests/<request_id>
Content-Type: application/json
{
  "status": "IN_PROGRESS",
  "assigned_officers": 3
}

# Delete patrol request
DELETE /api/patrol-requests/<request_id>
```

**Required Fields:**
- `ward_no` (integer)
- `district_code` (integer)
- `community_code` (string)
- `patrol_area` (string)
- `priority` (string)

**Optional Fields:**
- `reason` (string)
- `requested_by` (string)
- `assigned_officers` (integer, default: 0)
- `status` (string, default: "PENDING")
- `perimeter_radius` (float)

**Database Table:** `patrol_requests`

**Location:**
- **Code:** `app/routes.py` (lines 150-220)
- **CRUD Operations:** All in `routes.py` API functions
- **Database:** `app/database.py` (schema and sync functions)
- **CSV Sync:** `patrol_requests.csv` (auto-synced from database)

---

## 🌐 API Endpoints Summary

```bash
# Status check
GET /api/status

# Data Ingestion (Use Case 1)
GET /api/ingest
POST /api/ingest

# Dashboard Summary
GET /api/statistics

# Use Case Analysis
GET /api/analyse?case=1  # Crime Type Analysis
GET /api/analyse?case=2  # Arrest & Crime Outcomes Analysis
GET /api/analyse?case=3  # Time & Statistical Analysis
GET /api/analyse?case=4  # Geographic & Reporting Analysis

# Patrol Requests CRUD
GET /api/patrol-requests
POST /api/patrol-requests
GET /api/patrol-requests/<request_id>
PUT /api/patrol-requests/<request_id>
DELETE /api/patrol-requests/<request_id>
```

---

## 💾 Database

### SQLite (Default Local Database)
- **Location:** `database/chicago_crime.db`
- **Tables:**
  - `crimes` - Main crime data with engineered features
  - `crime_summary` - Summary statistics
  - `yearly_crime_summary` - Yearly aggregates
  - `community_crime_summary` - Community-level data
  - `district_crime_summary` - District-level data
  - `patrol_requests` - Patrol request records

### Database Views
- `vw_crime_overview` - Crime overview metrics
- `vw_crime_yearly` - Crime count by year
- `vw_yearly_crime` - Crime count per year (alternate)
- `vw_crime_by_category` - Top 5 crime types with percentages
- `vw_top_crimes` - Top 10 crime types

### MySQL Configuration (Optional)
To enable MySQL instead of SQLite:
1. Update `app/config.py` with MySQL credentials
2. Set `MYSQL_USE = True`
3. Ensure MySQL server is running

---

## 📁 Input Data Files

Raw CSV files are located in `Chicago_Datasets_Python/`:

- `chicago_crime_dataset.csv` - Main crime data
- `chicago_city_community.csv` - Community information
- `chicago_district_ps_info.csv` - District police info
- `chicago_police_beat_info.csv` - Police beat details
- `chicago_ward_offices.csv` - Ward office info
- `iucr_codes.csv` - IUCR code mappings
- `patrol_requests.csv` - Patrol request records

---

## 📊 Output Files

### Generated Charts
Location: `outputs/charts/`

**Use Case 2 Charts:**
- Crime trend over years
- Crime distribution by category
- Top 10 community areas
- Heatmap by month & day of week
- Yearly arrest rates

**Use Case 3 Charts:**
- Hourly crime distribution
- Community area outliers (box plot)
- Feature correlation matrix

**Use Case 4 Charts:**
- MySQL crime count per year
- MySQL top 5 crime types

### Generated Reports
Location: `outputs/reports/`

CSV files with aggregated statistics (as listed in Use Case 4 section)

---

## 🔍 Key Modules

### `app/analysis.py`
Exploratory analysis functions (Use Case 2 + helpers)
- `get_statistics()` - Dashboard summary
- `crime_summary()` - Overall crime overview
- `yearly_trend()` - Crime trends by year
- `top_communities()` - Top community areas
- `crime_by_district()` - District-level analysis
- `case1_crime_type_analysis()` - Use Case 1 analysis
- `case2_arrest_analysis()` - Use Case 2 analysis
- `case3_time_analysis()` - Use Case 3 analysis
- `case4_geographic_analysis()` - Use Case 4 analysis

### `app/statistics.py`
Statistical analysis functions (Use Case 3)
- `hourly_statistics()` - Crimes by hour
- `peak_hour()` - Peak crime hour
- `community_statistics()` - Community-level stats
- `community_area_outliers()` - Outlier detection
- `correlation_matrix()` - Feature correlation
- `numerical_statistics()` - Descriptive stats
- `iqr_outliers()` - IQR-based outlier detection
- `run_use_case_3()` - Complete Use Case 3 pipeline

### `app/reporting.py`
MySQL reporting functions (Use Case 4)
- `create_reporting_tables()` - Create summary tables
- `create_views()` - Create database views
- `get_reporting_summary()` - Query aggregated data
- `generate_report_files()` - Export reports to CSV
- `ensure_report_directory()` - Manage report directory
- `run_use_case_4()` - Complete Use Case 4 pipeline

### `app/visualization.py`
Chart creation for all use cases
- Use Case 2 charts: crime trends, distributions, heatmaps
- Use Case 3 charts: hourly patterns, outliers, correlations
- Use Case 4 charts: MySQL view-based visualizations
- Utility functions: `save_figure()`, `ensure_output_directory()`

### `app/database.py`
Database operations and patrol requests CRUD
- `get_connection()` - Database connection
- `ensure_patrol_requests_table()` - Create patrol table
- `initialize_patrol_requests_from_csv()` - Load patrol data
- `sync_patrol_requests_to_csv()` - Export patrol data to CSV
- `table_exists()` - Check table existence
- `get_row_count()` - Get crime data row count

### `app/ingestion.py`
Data ingestion pipeline (Use Case 1)
- `ingest_data()` - Main ingestion function
- `load_csv()` - Load CSV data
- Data cleaning and transformation routines

### `app/routes.py`
Flask API endpoints
- `@api.route("/api/status")` - Status check
- `@api.route("/api/ingest")` - Data ingestion
- `@api.route("/api/statistics")` - Dashboard summary
- `@api.route("/api/analyse")` - Analysis by case
- Patrol requests CRUD endpoints

---

## 🛠️ Configuration

**File:** `app/config.py`

Key configuration variables:
- `DATABASE_PATH` - SQLite database location
- `CRIME_CSV` - Raw crime data CSV path
- `CHARTS_DIR` - Output charts directory
- `REPORTS_DIR` - Output reports directory
- `MYSQL_USE` - Enable/disable MySQL
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB` - MySQL credentials

---

## 📈 Workflow Example

### Complete Analysis Pipeline:

```python
# 1. Ingest Data (Use Case 1)
curl http://localhost:5000/api/ingest

# 2. Get Dashboard Summary
curl http://localhost:5000/api/statistics

# 3. Exploratory Analysis (Use Case 2)
curl http://localhost:5000/api/analyse?case=2

# 4. Statistical Analysis (Use Case 3)
curl http://localhost:5000/api/analyse?case=3

# 5. Reporting (Use Case 4)
curl http://localhost:5000/api/analyse?case=4

# 6. View Generated Charts
ls outputs/charts/

# 7. View Generated Reports
ls outputs/reports/
```

---

## 📚 Technologies Used

- **Backend:** Flask (Python web framework)
- **Data Processing:** Pandas, NumPy
- **Visualization:** Matplotlib, Seaborn
- **Database:** SQLite (local), MySQL (optional)
- **Frontend:** HTML, CSS, JavaScript
- **Data Format:** CSV

---

## 🤝 Contributing

To extend this project:

1. Add new analysis functions to appropriate modules
2. Create corresponding visualization functions
3. Add new API endpoints to `routes.py`
4. Update database schema if needed
5. Document changes in this README

---

## 📝 License

This project is for educational purposes.

---

## 🆘 Troubleshooting

### Database Connection Issues
- Ensure SQLite file path is correct in `config.py`
- Check file permissions in `database/` directory
- For MySQL, verify connection credentials

### Missing Output Files
- Ensure `outputs/charts/` and `outputs/reports/` directories exist
- Check write permissions for output directories
- Review error logs in terminal output

### Data Loading Errors
- Verify CSV files exist in `Chicago_Datasets_Python/`
- Check CSV file format and encoding (UTF-8)
- Review column names match expected format

---

## 📞 Support

For issues or questions:
1. Check this README documentation
2. Review use case descriptions for expected outputs
3. Check console output for error messages
4. Verify database connectivity

---

**Last Updated:** August 2026
**Version:** 1.0
