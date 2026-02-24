# 🏗️ Databricks Medallion Architecture - Data Engineering Project

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.5-orange.svg)](https://spark.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.1-green.svg)](https://delta.io/)
[![Pandas](https://img.shields.io/badge/Pandas-3.0-red.svg)](https://pandas.pydata.org/)

> Production-grade implementation of the Medallion Architecture pattern for IoT sensor data processing with Bronze, Silver, and Gold layers.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Results & Metrics](#results--metrics)
- [What I Learned](#what-i-learned)

---

## 🎯 Overview

This project demonstrates a complete **Medallion Architecture** implementation (Bronze → Silver → Gold) for processing IoT sensor data. It showcases data engineering best practices including data quality management, incremental processing, and production-ready code structure.

**Business Use Case:** Real-time IoT sensor monitoring system for industrial facilities tracking temperature, humidity, pressure, and light levels across multiple locations.

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEDALLION ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📥 Raw Data (JSON)                                          │
│       │                                                       │
│       ▼                                                       │
│  🟤 BRONZE LAYER (Raw Ingestion)                            │
│       │  • Preserve original data                            │
│       │  • Add ingestion metadata                            │
│       │  • Delta Lake format                                 │
│       ▼                                                       │
│  ⚪ SILVER LAYER (Cleaned & Validated)                      │
│       │  • Data quality checks                               │
│       │  • Remove duplicates                                 │
│       │  • Handle nulls & outliers                           │
│       │  • Standardize formats                               │
│       ▼                                                       │
│  🟡 GOLD LAYER (Business Analytics)                         │
│       │  • Daily aggregations                                │
│       │  • Device health metrics                             │
│       │  • Location analytics                                │
│       │  • Hourly trends                                     │
│       ▼                                                       │
│  📊 Analytics & Reporting                                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Bronze Layer
- ✅ Raw JSON data ingestion with full fidelity
- ✅ Automatic metadata addition (ingestion timestamp, source file)
- ✅ Partitioned Parquet storage with Snappy compression
- ✅ Append-only writes preserving data lineage

### Silver Layer
- ✅ Comprehensive data quality validation
- ✅ Duplicate detection and removal
- ✅ Null value handling and flagging
- ✅ Out-of-range detection (115 anomalies identified)
- ✅ Battery health monitoring
- ✅ Quality scoring (achieved 96.97% quality rate)

### Gold Layer
- ✅ **5 Analytics Tables:**
  - Daily sensor averages by location (160 aggregations)
  - Device health metrics (50 devices monitored)
  - Location performance summary (5 facilities)
  - Hourly sensor trends (96 time-series records)
  - Data quality metrics (8-day tracking)

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Languages** | Python 3.12 |
| **Data Processing** | Pandas 3.0, PySpark 3.5 (cloud-ready) |
| **Storage** | Delta Lake, Parquet, PyArrow |
| **Data Generation** | Faker library |
| **Version Control** | Git, GitHub |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ 
- Java 11+ (for PySpark)
- 2GB free disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/databricks-medallion-architecture.git
cd databricks-medallion-architecture

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\Activate.ps1
# Or (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements-minimal.txt pyarrow

# Navigate to project
cd databricks-medallion
```

### Run the Pipeline

```bash
# Step 1: Generate 10,000 test records
python generate_sample_data.py

# Step 2: Ingest raw data (Bronze Layer)
python 01_bronze_layer_pandas.py

# Step 3: Clean & validate (Silver Layer)
python 02_silver_layer_pandas.py

# Step 4: Create analytics (Gold Layer)
python 03_gold_layer_pandas.py
```

**Expected Runtime:** ~2-3 minutes for complete pipeline

**Expected Output:**
- ✅ 10 JSON batch files in `data/sample/`
- ✅ Bronze layer: 10,000 records ingested
- ✅ Silver layer: 9,697 valid records (96.97% quality)
- ✅ Gold layer: 5 analytics tables created

---

## 📁 Project Structure

```
databricks-medallion-architecture/
├── README.md                          # This file
├── PROJECT_COMPLETE.md                # Detailed completion report
├── requirements-minimal.txt           # Python dependencies
├── LEARNING_GUIDE.md                  # Technical concepts explained
│
└── databricks-medallion/              # Main project
    ├── generate_sample_data.py       # Data generator (10K records)
    ├── 01_bronze_layer_pandas.py     # Bronze layer processor
    ├── 02_silver_layer_pandas.py     # Silver layer processor
    ├── 03_gold_layer_pandas.py       # Gold layer processor
    │
    ├── notebooks/                     # PySpark versions (cloud-ready)
    │   ├── 00_setup_environment.py
    │   ├── 01_bronze_layer.py
    │   ├── 02_silver_layer.py
    │   └── 03_gold_layer.py
    │
    ├── src/                           # Reusable modules
    │   ├── config/config.py          # Configuration management
    │   ├── utils/
    │   │   ├── spark_utils.py        # Spark helper functions
    │   │   └── data_generator.py     # Data generation utilities
    │   └── quality/
    │       └── validators.py         # Data quality framework
    │
    └── data/                          # Data layers (gitignored)
        ├── sample/                    # Generated test data
        ├── bronze/                    # Raw ingestion layer
        ├── silver/                    # Cleaned data layer
        └── gold/                      # Analytics layer
```

---

## 📊 Results & Metrics

### Pipeline Performance
- **Total Records Processed:** 10,000
- **Processing Time:** ~30 seconds end-to-end
- **Data Quality Score:** 96.97%
- **Storage Efficiency:** 1.67 MB (compressed Parquet)

### Data Quality Insights
| Metric | Count | Percentage |
|--------|-------|------------|
| Valid Records | 9,697 | 96.97% |
| Null Values Detected | 188 | 1.88% |
| Out-of-Range Values | 115 | 1.15% |
| Duplicates Found | 0 | 0.00% |

### Business Insights
- **50 IoT devices** monitored across **5 locations**
- **4 sensor types:** Temperature, Humidity, Pressure, Light
- **7-day** time span of sensor readings
- **All devices** in WARNING health status (avg 59.7% battery)

---

## 📚 What I Learned

Through this project, I gained hands-on experience with:

### 1. Data Architecture Patterns
- Medallion Architecture (Bronze/Silver/Gold layers)
- Data lakehouse concepts
- Incremental data processing strategies
- Data partitioning for performance

### 2. Data Quality Engineering
- Implementing validation rules and quality gates
- Outlier and anomaly detection algorithms
- Quality score calculation and tracking
- Handling missing and malformed data

### 3. Performance Optimization
- Parquet columnar storage benefits
- Snappy compression techniques
- Data partitioning strategies
- Memory-efficient pandas operations

### 4. Production Best Practices
- Modular code structure with reusable components
- Configuration management
- Comprehensive error handling
- Documentation and runbooks

---

## 🔄 PySpark vs Pandas Versions

This project includes **two implementations**:

### ✅ Pandas Version (Current - Windows Compatible)
- Located in root: `01_bronze_layer_pandas.py`, etc.
- Works on Windows with Python 3.12
- Perfect for local development and learning
- Demonstrates same concepts with simpler syntax

### 🌩️ PySpark Version (Cloud-Ready)
- Located in `notebooks/` folder
- Designed for Databricks or Spark clusters
- Scales to billions of records
- Production deployment ready

**Why Two Versions?**
PySpark 3.5+ has compatibility issues on Windows with Python 3.12 due to subprocess handling. The pandas version demonstrates the same architectural patterns and is perfect for portfolios and interviews, while the PySpark version is ready for cloud deployment.

---

## 🎯 Key Takeaways

This project demonstrates:

✅ **End-to-End Data Engineering** - Complete pipeline from raw data to business analytics  
✅ **Data Quality Focus** - 97% quality achieved through systematic validation  
✅ **Production-Ready Code** - Modular, documented, and maintainable  
✅ **Modern Architecture** - Industry-standard medallion pattern  
✅ **Practical Skills** - Immediately applicable to real data engineering roles  

---

## 📖 Additional Documentation

- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - Detailed project completion report
- [LEARNING_GUIDE.md](LEARNING_GUIDE.md) - Deep dive into technical concepts
- [databricks-medallion/README.md](databricks-medallion/README.md) - Project-specific documentation
- [CHECKLIST.md](CHECKLIST.md) - Development checklist

---

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome! Feel free to:
- Open issues for bugs or improvements
- Share how you've adapted this pattern
- Suggest additional features or analytics

---

## 📬 Contact

**Saksham** - Data Engineering Enthusiast  
📧 Email: sakshamc90@gmail.com  
💼 GitHub: [@wad-saksham](https://github.com/wad-saksham)

---

## 📄 License

This project is open source and available under the MIT License.

---

**⭐ If you found this project helpful, please consider giving it a star!**
