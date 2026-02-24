# 🏅 Databricks Medallion Architecture Project

> Production-grade data lakehouse implementation using Databricks' Medallion Architecture pattern with Bronze-Silver-Gold layers.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![PySpark](https://img.shields.io/badge/PySpark-3.5.0-orange.svg)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-3.0.0-red.svg)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Key Features](#key-features)
- [Learning Outcomes](#learning-outcomes)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

This project demonstrates a **production-ready data lakehouse** implementation using the Medallion Architecture pattern. The pipeline processes IoT sensor data through three progressive layers:

- **Bronze Layer**: Raw data ingestion with auditability
- **Silver Layer**: Cleaned, validated, and conformed data
- **Gold Layer**: Business-ready aggregations for analytics

### Business Use Case

Monitoring and analyzing IoT sensor data from manufacturing facilities to detect anomalies, track performance metrics, and optimize operations.

---

## 🏗️ Architecture

### Medallion Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                         │
│                    (IoT Sensors, APIs, Files)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      BRONZE LAYER (Raw)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Exact copy of source data                          │  │
│  │ • Append-only Delta tables                           │  │
│  │ • Includes ingestion metadata                        │  │
│  │ • Schema validation on write                         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     SILVER LAYER (Refined)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Data cleansing (nulls, duplicates)                 │  │
│  │ • Type casting and format standardization            │  │
│  │ • Business rule validation                           │  │
│  │ • Data quality checks                                │  │
│  │ • Incremental merge using Delta                      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      GOLD LAYER (Curated)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Pre-aggregated metrics                             │  │
│  │ • Denormalized for query performance                 │  │
│  │ • Business-level transformations                     │  │
│  │ • Ready for BI tools and ML                          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    ANALYTICS & BI LAYER                      │
│              (Dashboards, Reports, ML Models)               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Ingestion**: IoT sensor data arrives as JSON files in S3
2. **Bronze**: Raw data loaded into Delta Lake with metadata
3. **Silver**: Data cleaned, deduplicated, and validated
4. **Gold**: Aggregated metrics for analytics use cases
5. **Consumption**: Business users query Gold tables for insights

---

## 🛠️ Technologies

| Technology             | Version   | Purpose                        |
| ---------------------- | --------- | ------------------------------ |
| **Python**             | 3.9+      | Primary programming language   |
| **PySpark**            | 3.5.0     | Distributed data processing    |
| **Delta Lake**         | 3.0.0     | ACID transactions, time travel |
| **Databricks**         | Community | Unified analytics platform     |
| **AWS S3**             | -         | Cloud object storage           |
| **Boto3**              | 1.28+     | AWS SDK for Python             |
| **Great Expectations** | 0.18+     | Data quality validation        |

---

## 📁 Project Structure

```
databricks-medallion/
│
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
│
├── notebooks/                         # Databricks notebooks
│   ├── 00_setup_environment.py       # Initial setup and config
│   ├── 01_bronze_layer.py            # Raw data ingestion
│   ├── 02_silver_layer.py            # Data cleansing & validation
│   ├── 03_gold_layer.py              # Business aggregations
│   └── 04_data_quality_checks.py     # Quality validation
│
├── src/                               # Reusable Python modules
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py                 # Configuration management
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── spark_utils.py            # Spark helper functions
│   │   ├── delta_utils.py            # Delta Lake operations
│   │   └── data_generator.py         # Sample data generation
│   │
│   └── quality/
│       ├── __init__.py
│       ├── validators.py             # Data quality checks
│       └── expectations.py           # Great Expectations suite
│
├── data/
│   └── sample/                        # Sample data for testing
│       ├── iot_sensors_sample.json
│       └── README.md
│
├── tests/                             # Unit tests
│   ├── __init__.py
│   ├── test_transformations.py
│   └── test_quality_checks.py
│
└── docs/                              # Documentation
    ├── architecture_diagram.md
    ├── data_dictionary.md
    └── deployment_guide.md
```

---

## ⚙️ Setup Instructions

### Prerequisites

1. **Databricks Community Edition Account**
   - Sign up at: https://community.cloud.databricks.com/

2. **AWS Free Tier Account**
   - Sign up at: https://aws.amazon.com/free/

3. **Local Development Tools**

   ```powershell
   # Python 3.9+
   python --version

   # Git
   git --version
   ```

### Installation Steps

#### 1. Clone Repository

```powershell
cd "c:\Users\saksh\OneDrive\Desktop\Data enginnering project"
```

#### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 3. Install Dependencies

```powershell
pip install -r ../requirements.txt
```

#### 4. Configure AWS Credentials

```powershell
aws configure
# Enter your AWS Access Key, Secret Key, and region (us-east-1)
```

#### 5. Create S3 Bucket

```powershell
aws s3 mb s3://your-name-medallion-demo
```

#### 6. Update Configuration

```python
# Edit src/config/config.py
BUCKET_NAME = "your-name-medallion-demo"
AWS_REGION = "us-east-1"
```

---

## 🚀 Usage

### Option 1: Run Locally (Testing)

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to project
cd databricks-medallion

# Generate sample data
python src/utils/data_generator.py

# Run Bronze layer (local mode)
python notebooks/01_bronze_layer.py

# Run Silver layer
python notebooks/02_silver_layer.py

# Run Gold layer
python notebooks/03_gold_layer.py

# Run quality checks
python notebooks/04_data_quality_checks.py
```

### Option 2: Run on Databricks (Production)

1. **Upload Notebooks**
   - Login to Databricks workspace
   - Navigate to Workspace → Import
   - Upload all files from `notebooks/` folder

2. **Upload Source Code**
   - Create folder: `/Workspace/Users/your-email/medallion-project/`
   - Upload `src/` directory

3. **Create Cluster**
   - Runtime: 13.3 LTS (Scala 2.12, Spark 3.4.1)
   - Node Type: Single node (for Community Edition)

4. **Run Notebooks in Order**
   - Execute: `00_setup_environment`
   - Execute: `01_bronze_layer`
   - Execute: `02_silver_layer`
   - Execute: `03_gold_layer`
   - Execute: `04_data_quality_checks`

5. **Schedule Jobs** (if available)
   - Go to Workflows → Create Job
   - Add notebook tasks
   - Set schedule (daily/hourly)

---

## ✨ Key Features

### 1. **ACID Transactions with Delta Lake**

```python
# Atomic writes ensure data consistency
df.write
    .format("delta")
    .mode("append")
    .save(bronze_path)
```

### 2. **Incremental Processing**

```python
# Process only new data since last run
deltaTable.alias("target").merge(
    source.alias("source"),
    "target.sensor_id = source.sensor_id AND target.timestamp = source.timestamp"
).whenNotMatchedInsertAll().execute()
```

### 3. **Time Travel**

```python
# Query historical versions
df_yesterday = spark.read
    .format("delta")
    .option("versionAsOf", 10)
    .load(silver_path)
```

### 4. **Data Quality Validation**

```python
# Automated quality checks
quality_checks = [
    ("null_rate_check", null_percentage < 5%),
    ("duplicate_check", duplicate_count == 0),
    ("schema_validation", schema_matches_expected)
]
```

### 5. **Schema Evolution**

```python
# Handle schema changes gracefully
df.write
    .format("delta")
    .option("mergeSchema", "true")
    .mode("append")
    .save(path)
```

### 6. **Partitioning for Performance**

```python
# Optimize queries with partitioning
df.write
    .format("delta")
    .partitionBy("date", "sensor_type")
    .save(gold_path)
```

---

## 🎓 Learning Outcomes

After completing this project, you will understand:

### Technical Skills

- ✅ Medallion Architecture design pattern
- ✅ Delta Lake ACID transactions
- ✅ PySpark DataFrame transformations
- ✅ Incremental data processing
- ✅ Data quality frameworks
- ✅ Cloud storage integration (S3)
- ✅ Databricks platform usage

### Best Practices

- ✅ Separation of concerns (Bronze/Silver/Gold)
- ✅ Schema validation and evolution
- ✅ Error handling and logging
- ✅ Configuration management
- ✅ Code modularity and reusability
- ✅ Testing data pipelines

### Interview Topics

- ✅ "Explain Medallion Architecture"
- ✅ "Why use Delta Lake over Parquet?"
- ✅ "How do you handle late-arriving data?"
- ✅ "Describe your data quality approach"
- ✅ "How do you optimize Spark performance?"

---

## 🔮 Future Enhancements

### Phase 2 (Streaming)

- [ ] Implement streaming ingestion with Structured Streaming
- [ ] Add watermarking for late data handling
- [ ] Real-time dashboard with live metrics

### Phase 3 (Orchestration)

- [ ] Apache Airflow DAGs for scheduling
- [ ] Monitoring and alerting with Databricks
- [ ] CI/CD pipeline with GitHub Actions

### Phase 4 (Advanced)

- [ ] Unity Catalog for data governance
- [ ] ML models on Gold layer data
- [ ] Advanced partitioning strategies
- [ ] Query optimization techniques

---

## 📊 Sample Queries

### Query Gold Layer Metrics

```sql
-- Top performing sensors by average reading
SELECT
    sensor_id,
    sensor_type,
    AVG(reading_value) as avg_reading,
    COUNT(*) as total_readings,
    MAX(reading_value) as max_reading
FROM gold.sensor_metrics_daily
WHERE date >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY sensor_id, sensor_type
ORDER BY avg_reading DESC
LIMIT 10;
```

### Data Quality Report

```sql
-- Quality metrics by layer
SELECT
    layer,
    check_name,
    passed,
    check_timestamp
FROM quality.validation_results
WHERE DATE(check_timestamp) = CURRENT_DATE
ORDER BY check_timestamp DESC;
```

---

## 🤝 Contributing

This is a portfolio project, but feedback and suggestions are welcome!

---

## 📜 License

MIT License - Feel free to use this for learning purposes.

---

## 👤 Author

**Your Name**

- LinkedIn: [your-linkedin]
- GitHub: [your-github]
- Email: [your-email]

---

## 🙏 Acknowledgments

- Databricks documentation and community
- Apache Spark community
- Delta Lake contributors

---

**Built with ❤️ to demonstrate modern data engineering skills**
