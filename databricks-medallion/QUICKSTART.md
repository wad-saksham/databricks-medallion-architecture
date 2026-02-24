# 🚀 QUICK START GUIDE

### Get the Medallion Architecture Project Running in 15 Minutes

---

## ⚡ Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.9 or higher installed
- ✅ At least 4GB RAM available
- ✅ 2GB free disk space

---

## 📥 Step 1: Install Dependencies (5 minutes)

Open PowerShell or Terminal in the project directory:

```powershell
# Navigate to project
cd "c:\Users\saksh\OneDrive\Desktop\Data enginnering project"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1

# On Mac/Linux:
# source venv/bin/activate

# Install required packages
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected time:** 3-5 minutes (depending on internet speed)

---

## 🎬 Step 2: Run Setup (3 minutes)

This will generate sample data and verify everything is working:

```powershell
# Make sure virtual environment is activated (you should see (venv) in prompt)

# Navigate to project directory
cd databricks-medallion

# Run setup script
python notebooks/00_setup_environment.py
```

**What this does:**

- ✅ Verifies Spark installation
- ✅ Tests Delta Lake functionality
- ✅ Generates sample IoT sensor data
- ✅ Creates necessary directories
- ✅ Displays configuration

**Expected output:**

```
===============================================================================
MEDALLION ARCHITECTURE - ENVIRONMENT SETUP
===============================================================================
...
✅ ENVIRONMENT SETUP COMPLETE!
```

---

## 🏗️ Step 3: Run the Pipeline (7 minutes)

Run the three layers in sequence:

### Bronze Layer (Raw Ingestion)

```powershell
python notebooks/01_bronze_layer.py
```

**Time:** ~2 minutes  
**Output:** Raw data ingested into Bronze Delta tables

### Silver Layer (Data Cleansing)

```powershell
python notebooks/02_silver_layer.py
```

**Time:** ~3 minutes  
**Output:** Clean, validated data in Silver Delta tables

### Gold Layer (Business Aggregations)

```powershell
python notebooks/03_gold_layer.py
```

**Time:** ~2 minutes  
**Output:** Business-ready aggregated datasets

---

## ✅ Step 4: Verify Success

If everything worked, you should see:

```
✅ GOLD LAYER PROCESSING COMPLETE
🎉 MEDALLION ARCHITECTURE IMPLEMENTATION COMPLETE!
```

**Check your data folders:**

```
data/
├── bronze/        # Raw data with ingestion metadata
├── silver/        # Clean, validated data
└── gold/          # Business aggregations
    ├── sensor_metrics_daily/
    ├── sensor_metrics_hourly/
    └── sensor_anomalies/
```

---

## 🎯 What You Just Built

You've created a production-grade data lakehouse with:

### Bronze Layer

- 📥 Ingested 10,000+ IoT sensor readings
- 📝 Added metadata for data lineage
- 💾 Stored in Delta Lake format with ACID guarantees

### Silver Layer

- 🧹 Cleaned and deduplicated data
- ✅ Validated timestamps and data quality
- 🚨 Flagged anomalous readings
- 📊 Calculated quality scores

### Gold Layer

- 📈 Daily sensor metrics with health scores
- ⏰ Hourly time-series aggregations
- 🚨 Anomaly detection alerts
- 📊 Business-ready analytics

---

## 🎓 Understanding What You Built

### Data Flow

```
JSON Files → Bronze → Silver → Gold → Analytics/BI
   (Raw)    (Ingest) (Clean)  (Aggregate)
```

### Key Features Demonstrated

1. **ACID Transactions** - Delta Lake ensures data consistency
2. **Incremental Processing** - Only process new/changed data
3. **Time Travel** - Query historical versions of data
4. **Data Quality** - Automated validation and checks
5. **Partitioning** - Optimized query performance
6. **Schema Evolution** - Handle schema changes gracefully

---

## 📊 Explore Your Data

### Query Bronze Layer

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Explore").getOrCreate()

df = spark.read.format("delta").load("data/bronze/sensor_data_raw")
df.show()
df.count()  # Total raw records
```

### Query Silver Layer

```python
df = spark.read.format("delta").load("data/silver/sensor_data_clean")
df.filter("quality_score >= 75").show()  # High quality data only
```

### Query Gold Layer

```python
# Daily metrics
df = spark.read.format("delta").load("data/gold/sensor_metrics_daily")
df.orderBy("date").show()

# Anomalies
df_anomalies = spark.read.format("delta").load("data/gold/sensor_anomalies")
df_anomalies.filter("severity == 'CRITICAL'").show()
```

---

## 🔍 Common Issues & Solutions

### Issue 1: Import Errors

```
ModuleNotFoundError: No module named 'pyspark'
```

**Solution:** Make sure virtual environment is activated

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue 2: Java Not Found

```
Java gateway process exited before sending its port number
```

**Solution:** Install Java 11+

- Download from: https://adoptium.net/
- Set JAVA_HOME environment variable

### Issue 3: Path Errors

```
FileNotFoundError: data/sample/historical
```

**Solution:** Run setup script first

```powershell
python notebooks/00_setup_environment.py
```

### Issue 4: Delta Lake Errors

```
Delta table not found
```

**Solution:** Run layers in order: Bronze → Silver → Gold

---

## 🚀 Next Steps

### 1. Modify the Data

Edit `src/utils/data_generator.py` to:

- Change sensor types
- Adjust anomaly rates
- Generate more data

### 2. Add New Metrics

Edit `notebooks/03_gold_layer.py` to:

- Create new aggregations
- Add business calculations
- Build custom reports

### 3. Connect to BI Tools

- Export Gold tables to CSV
- Connect Power BI to Delta tables
- Create visualizations

### 4. Deploy to Databricks

See `databricks-medallion/docs/deployment_guide.md` for:

- Uploading to Databricks workspace
- Creating jobs and schedules
- Setting up monitoring

---

## 📚 Learning Resources

### Included in This Project:

- `LEARNING_GUIDE.md` - Deep dive into concepts
- `MASTER_ROADMAP.md` - Project roadmap and phases
- `README.md` - Full project documentation

### External Resources:

- **Delta Lake:** https://docs.delta.io/
- **PySpark:** https://spark.apache.org/docs/latest/api/python/
- **Databricks:** https://docs.databricks.com/

---

## 🤔 Understanding Each Layer

### When to Use Bronze

- **Purpose:** Archive and audit
- **Users:** Data engineers for debugging
- **Query Pattern:** Historical reprocessing

### When to Use Silver

- **Purpose:** Feature engineering and ML
- **Users:** Data scientists
- **Query Pattern:** Complex analytical queries

### When to Use Gold

- **Purpose:** Business reporting
- **Users:** Business analysts, dashboards
- **Query Pattern:** Simple aggregation queries

---

## 🎯 Interview Talking Points

After completing this, you can say:

> "I built a production-grade data lakehouse using Databricks' Medallion Architecture. The pipeline processes IoT sensor data through Bronze, Silver, and Gold layers using PySpark and Delta Lake. I implemented incremental processing with ACID guarantees, automated data quality checks, and created business-ready aggregations optimized for analytics workloads."

**Key metrics to mention:**

- Processed 10,000+ sensor readings
- Implemented 3-layer Medallion Architecture
- Used Delta Lake for ACID transactions
- Created automated quality validation
- Built 3 Gold-layer analytics tables

---

## ✅ Success Checklist

After running everything, you should have:

- [x] Generated sample IoT sensor data
- [x] Bronze layer with raw data and metadata
- [x] Silver layer with cleaned, validated data
- [x] Gold layer with business aggregations
- [x] Data quality validation reports
- [x] Optimized Delta tables
- [x] Understanding of Medallion Architecture

---

## 🎉 Congratulations!

You've successfully built a production-grade data engineering project that demonstrates:

✅ Modern data architecture patterns  
✅ Cloud-ready data engineering  
✅ Real-world data quality practices  
✅ Scalable distributed processing  
✅ Business analytics readiness

**This project showcases skills that directly align with the job you're targeting!**

---

## 💬 Need Help?

If you encounter issues:

1. Check the console output for error messages
2. Review the `LEARNING_GUIDE.md` for concept explanations
3. Verify all prerequisites are installed
4. Make sure you're running scripts in the correct order

---

**Ready for Production Deployment?** See `docs/deployment_guide.md`  
**Want to Understand the Code?** See `LEARNING_GUIDE.md`  
**Planning Next Steps?** See `MASTER_ROADMAP.md`

---

🚀 **Now go build your second project - the Retail Analytics Platform!**
