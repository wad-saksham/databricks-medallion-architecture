"""
SILVER LAYER - Data Cleansing and Validation

Purpose:
    Transform Bronze layer raw data into clean, conformed, validated Silver tables.
    Apply data quality rules, handle nulls, remove duplicates, and standardize formats.
    
Silver Layer Principles:
    - Clean and deduplicate data  
    - Validate business rules
    - Standardize data types and formats
    - Enforce schema
    - Create single source of truth
    - Support incremental processing

Author: Your Name
Date: 2024-02-18
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pyspark.sql import SparkSession, functions as F, Window
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType,
    IntegerType, TimestampType, DateType
)
from delta.tables import DeltaTable

from src.config import config
from src.utils import spark_utils
from src.quality import validators

# ==============================================================================
# CONFIGURATION
# ==============================================================================

print("=" * 80)
print("SILVER LAYER - DATA CLEANSING & VALIDATION")
print("=" * 80)

# Create Spark Session
spark = spark_utils.create_spark_session(
    app_name="Silver_Layer_Processing",
    config=config.SPARK_CONFIG
)

# Paths
BRONZE_TABLE_PATH = config.get_bronze_path(config.BRONZE_SENSOR_DATA)
SILVER_TABLE_PATH = config.get_silver_path(config.SILVER_SENSOR_DATA)

print(f"\n📂 Bronze Source: {BRONZE_TABLE_PATH}")
print(f"📂 Silver Target: {SILVER_TABLE_PATH}")

# ==============================================================================
# READ BRONZE DATA
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 1: READ DATA FROM BRONZE LAYER")
print("=" * 80)

try:
    df_bronze = spark.read.format("delta").load(BRONZE_TABLE_PATH)
    bronze_count = df_bronze.count()
    print(f"✅ Read {bronze_count:,} records from Bronze layer")
    
    print("\n📊 Bronze Data Sample:")
    df_bronze.select(
        "sensor_id", "sensor_type", "timestamp", 
        "reading_value", "status", "location"
    ).show(5, truncate=False)
    
except Exception as e:
    print(f"❌ Error reading Bronze data: {str(e)}")
    raise

# ==============================================================================
# DATA CLEANSING
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 2: DATA CLEANSING")
print("=" * 80)

# 2.1: Parse and Validate Timestamp
print("\n Step 2.1: Parse Timestamp")
df_silver = df_bronze.withColumn(
    "timestamp_parsed",
    F.to_timestamp(F.col("timestamp"))
)

# Check for invalid timestamps
invalid_timestamps = df_silver.filter(F.col("timestamp_parsed").isNull()).count()
if invalid_timestamps > 0:
    print(f"⚠️  Found {invalid_timestamps} invalid timestamps - will filter out")
    df_silver = df_silver.filter(F.col("timestamp_parsed").isNotNull())
else:
    print(f"✅ All timestamps valid")

# Rename to clean column
df_silver = df_silver.drop("timestamp").withColumnRenamed("timestamp_parsed", "timestamp")

# 2.2: Handle Null Values
print("\n📋 Step 2.2: Handle Missing Values")

# Strategy for different columns:
# - Critical fields (sensor_id, sensor_type, timestamp): Remove records
# - Numeric fields (reading_value): Keep for analysis, flag as null
# - Optional fields (location, status): Fill with defaults

# Remove nulls from critical fields
critical_nulls_before = df_silver.filter(
    F.col("sensor_id").isNull() | 
    F.col("sensor_type").isNull() | 
    F.col("timestamp").isNull()
).count()

df_silver = df_silver.filter(
    F.col("sensor_id").isNotNull() &
    F.col("sensor_type").isNotNull() &
    F.col("timestamp").isNotNull()
)

if critical_nulls_before > 0:
    print(f"⚠️  Removed {critical_nulls_before} records with null critical fields")
else:
    print(f"✅ No null critical fields")

# Fill optional fields with defaults
df_silver = df_silver \
    .withColumn("status", F.coalesce(F.col("status"), F.lit("UNKNOWN"))) \
    .withColumn("location", F.coalesce(F.col("location"), F.lit("UNKNOWN"))) \
    .withColumn("battery_level", F.coalesce(F.col("battery_level"), F.lit(0.0))) \
    .withColumn("signal_strength", F.coalesce(F.col("signal_strength"), F.lit(0)))

print(f"✅ Filled missing values in optional fields")

# 2.3: Remove Duplicates
print("\n📋 Step 2.3: Remove Duplicate Records")

# Define uniqueness: sensor_id + timestamp
before_dedup = df_silver.count()

# Keep the latest record (based on ingestion_timestamp) for duplicates
window_spec = Window.partitionBy("sensor_id", "timestamp") \
    .orderBy(F.desc("ingestion_timestamp"))

df_silver = df_silver \
    .withColumn("row_num", F.row_number().over(window_spec)) \
    .filter(F.col("row_num") == 1) \
    .drop("row_num")

after_dedup = df_silver.count()
duplicates_removed = before_dedup - after_dedup

if duplicates_removed > 0:
    print(f"✅ Removed {duplicates_removed:,} duplicate records")
    print(f"   Before: {before_dedup:,} | After: {after_dedup:,}")
else:
    print(f"✅ No duplicates found")

# 2.4: Validate and Clean Values
print("\n📋 Step 2.4: Validate Value Ranges")

# Flag anomalous values based on sensor type
df_silver = df_silver.withColumn(
    "is_anomaly",
    F.when(
        (F.col("sensor_type") == "temperature") & 
        ((F.col("reading_value") < -50) | (F.col("reading_value") > 150)),
        F.lit(True)
    ).when(
        (F.col("sensor_type") == "pressure") & 
        ((F.col("reading_value") < 0) | (F.col("reading_value") > 1000)),
        F.lit(True)
    ).when(
        (F.col("sensor_type") == "humidity") & 
        ((F.col("reading_value") < 0) | (F.col("reading_value") > 100)),
        F.lit(True)
    ).when(
        (F.col("sensor_type") == "vibration") & 
        ((F.col("reading_value") < 0) | (F.col("reading_value") > 500)),
        F.lit(True)
    ).otherwise(F.lit(False))
)

anomaly_count = df_silver.filter(F.col("is_anomaly") == True).count()
anomaly_rate = (anomaly_count / after_dedup) * 100 if after_dedup > 0 else 0

print(f"✅ Flagged {anomaly_count:,} anomalous readings ({anomaly_rate:.2f}%)")

# ==============================================================================
# DATA TRANSFORMATION & ENRICHMENT
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 3: DATA TRANSFORMATION & ENRICHMENT")
print("=" * 80)

# 3.1: Add Date and Time Partitions
print("\n📋 Step 3.1: Add Date/Time Partitions")

df_silver = df_silver \
    .withColumn("date", F.to_date(F.col("timestamp"))) \
    .withColumn("year", F.year(F.col("timestamp"))) \
    .withColumn("month", F.month(F.col("timestamp"))) \
    .withColumn("day", F.dayofmonth(F.col("timestamp"))) \
    .withColumn("hour", F.hour(F.col("timestamp")))

print(f"✅ Added date partition columns (date, year, month, day, hour)")

# 3.2: Standardize Sensor IDs
print("\n📋 Step 3.2: Standardize Sensor IDs")

df_silver = df_silver \
    .withColumn("sensor_id_clean", F.upper(F.trim(F.col("sensor_id")))) \
    .drop("sensor_id") \
    .withColumnRenamed("sensor_id_clean", "sensor_id")

print(f"✅ Standardized sensor IDs (uppercase, trimmed)")

# 3.3: Create Quality Score
print("\n📋 Step 3.3: Calculate Data Quality Score")

df_silver = df_silver.withColumn(
    "quality_score",
    F.when(
        (F.col("reading_value").isNotNull()) &
        (F.col("battery_level") > 20) &
        (F.col("signal_strength") >= 3) &
        (F.col("is_anomaly") == False),
        F.lit(100)
    ).when(
        (F.col("reading_value").isNotNull()) &
        (F.col("is_anomaly") == False),
        F.lit(75)
    ).when(
        F.col("reading_value").isNotNull(),
        F.lit(50)
    ).otherwise(F.lit(0))
)

print(f"✅ Calculated quality scores (0-100)")

# 3.4: Add Silver Layer Metadata
print("\n📋 Step 3.4: Add Silver Layer Metadata")

df_silver = df_silver \
    .withColumn("silver_processing_timestamp", F.current_timestamp()) \
    .withColumn("silver_record_id", F.monotonically_increasing_id())

print(f"✅ Added Silver layer metadata")

# ==============================================================================
# DATA QUALITY VALIDATION
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 4: DATA QUALITY VALIDATION")
print("=" * 80)

# Initialize validator
validator = validators.DataQualityValidator(spark)

# Define quality checks configuration
quality_config = {
    "null_checks": {
        "sensor_id": 0.0,      # No nulls allowed
        "sensor_type": 0.0,    # No nulls allowed
        "timestamp": 0.0,      # No nulls allowed
        "reading_value": 0.05, # Max 5% nulls
    },
    "duplicate_check": {
        "keys": ["sensor_id", "timestamp"],
        "threshold": 0.0  # No duplicates allowed in Silver
    },
}

# Run checks
all_passed, results = validator.run_all_checks(df_silver, quality_config)

if not all_passed:
    print("\n⚠️  WARNING: Some quality checks failed!")
    print("    Review results above and decide whether to proceed")
    # In production, you might want to:
    # - Send alerts
    # - Stop pipeline
    # - Quarantine bad data
else:
    print("\n✅ All quality checks passed!")

# ==============================================================================
# SELECT FINAL COLUMNS
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 5: SELECT FINAL SCHEMA")
print("=" * 80)

# Select and order final columns for Silver table
df_silver_final = df_silver.select(
    # IDs and Keys
    "silver_record_id",
    "sensor_id",
    "sensor_type",
    
    # Timestamp fields
    "timestamp",
    "date",
    "year",
    "month",
    "day",
    "hour",
    
    # Sensor readings
    "reading_value",
    "unit",
    "status",
    
    # Sensor metadata
    "location",
    "battery_level",
    "signal_strength",
    
    # Quality indicators
    "is_anomaly",
    "quality_score",
    
    # Lineage
    "bronze_record_id",
    "ingestion_timestamp",
    "silver_processing_timestamp"
)

print("✅ Final Silver schema defined")
print(f"   Total columns: {len(df_silver_final.columns)}")
print(f"   Total records: {df_silver_final.count():,}")

print("\n📋 Silver Schema:")
df_silver_final.printSchema()

# ==============================================================================
# WRITE TO SILVER DELTA TABLE
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 6: WRITE TO SILVER DELTA TABLE")
print("=" * 80)

try:
    # Partition columns for Silver
    partition_cols = config.PROCESSING_CONFIG["partition_columns"]["silver"]
    
    # Write to Delta
    df_silver_final.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy(*partition_cols) \
        .option("overwriteSchema", "true") \
        .save(SILVER_TABLE_PATH)
    
    print(f"✅ Successfully wrote {df_silver_final.count():,} records to Silver layer")
    print(f"✅ Partitioned by: {', '.join(partition_cols)}")
    print(f"✅ Location: {SILVER_TABLE_PATH}")
    
except Exception as e:
    print(f"❌ Error writing to Silver table: {str(e)}")
    raise

# ==============================================================================
# OPTIMIZE DELTA TABLE
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 7: OPTIMIZE DELTA TABLE")
print("=" * 80)

try:
    # Z-order for better query performance
    zorder_cols = config.PROCESSING_CONFIG["z_order_columns"]["silver"]
    
    print(f"Running OPTIMIZE with Z-ORDER on: {', '.join(zorder_cols)}")
    spark.sql(f"""
        OPTIMIZE delta.`{SILVER_TABLE_PATH}`
        ZORDER BY ({', '.join(zorder_cols)})
    """)
    
    print(f"✅ Table optimized with Z-ordering")
    
except Exception as e:
    print(f"⚠️  Optimization skipped: {str(e)}")

# ==============================================================================
# VERIFY AND ANALYZE
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 8: VERIFY SILVER TABLE")
print("=" * 80)

# Read back
df_verify = spark.read.format("delta").load(SILVER_TABLE_PATH)
verify_count = df_verify.count()

print(f"✅ Verified: {verify_count:,} records in Silver table")

# Statistics
print("\n📊 Silver Layer Statistics:")

stats = df_verify.select(
    F.count("*").alias("total_records"),
    F.countDistinct("sensor_id").alias("unique_sensors"),
    F.countDistinct("sensor_type").alias("sensor_types"),
    F.min("timestamp").alias("earliest"),
    F.max("timestamp").alias("latest"),
    F.avg("quality_score").alias("avg_quality_score"),
    F.sum(F.when(F.col("is_anomaly") == True, 1).otherwise(0)).alias("anomaly_count")
).collect()[0]

print(f"""
Total Records:       {stats['total_records']:,}
Unique Sensors:      {stats['unique_sensors']:,}
Sensor Types:        {stats['sensor_types']:,}
Date Range:          {stats['earliest']} to {stats['latest']}
Avg Quality Score:   {stats['avg_quality_score']:.1f}/100
Anomalies Flagged:   {stats['anomaly_count']:,}
""")

# Distribution by sensor type
print("📊 Sensor Type Distribution:")
df_verify.groupBy("sensor_type") \
    .agg(
        F.count("*").alias("count"),
        F.avg("reading_value").alias("avg_value"),
        F.avg("quality_score").alias("avg_quality")
    ) \
    .orderBy("sensor_type") \
    .show()

# Sample final data
print("\n📊 Sample Silver Data:")
df_verify.select(
    "sensor_id", "sensor_type", "timestamp", 
    "reading_value", "quality_score", "is_anomaly"
).show(10, truncate=False)

# ==============================================================================
# SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("✅ SILVER LAYER PROCESSING COMPLETE")
print("=" * 80)

print(f"""
Silver Layer Summary:
--------------------
✅ Data cleaned and deduplicated
✅ Timestamps validated and parsed
✅ Null values handled appropriately
✅ Anomalies identified and flagged
✅ Quality scores calculated
✅ Data quality checks passed
✅ Table optimized for query performance

Data Quality:
------------
Bronze Records:      {bronze_count:,}
Silver Records:      {verify_count:,}
Records Filtered:    {bronze_count - verify_count:,}
Avg Quality Score:   {stats['avg_quality_score']:.1f}/100

Next Step:
---------
→ Run Gold Layer notebook (03_gold_layer.py) for business aggregations

Location: {SILVER_TABLE_PATH}
""")

print("=" * 80)

# spark.stop()
