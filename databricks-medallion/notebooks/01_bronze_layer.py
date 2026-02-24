"""
BRONZE LAYER - Raw Data Ingestion

Purpose:
    Ingest raw IoT sensor data from source (S3/local) into Bronze Delta tables.
    Store data exactly as received with minimal transformation.
    
Bronze Layer Principles:
    - Preserve original data exactly as received
    - Append-only (never delete or update)
    - Add ingestion metadata for lineage
    - Validate basic structure only
    - Enable reprocessing from scratch if needed

Author: Your Name
Date: 2024-02-18
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, 
    IntegerType, TimestampType
)

from src.config import config
from src.utils import spark_utils

# ==============================================================================
# CONFIGURATION
# ==============================================================================

print("=" * 80)
print("BRONZE LAYER - RAW DATA INGESTION")
print("=" * 80)

# Create Spark Session
spark = spark_utils.create_spark_session(
    app_name="Bronze_Layer_Ingestion",
    config=config.SPARK_CONFIG
)

# Paths
SOURCE_DATA_PATH = str(Path(__file__).parent.parent / "data" / "sample" / "historical")
BRONZE_TABLE_PATH = config.get_bronze_path(config.BRONZE_SENSOR_DATA)

print(f"\n📂 Source Path: {SOURCE_DATA_PATH}")
print(f"📂 Bronze Path: {BRONZE_TABLE_PATH}")

# ==============================================================================
# SCHEMA DEFINITION
# ==============================================================================

# Define expected schema for validation
RAW_SENSOR_SCHEMA = StructType([
    StructField("sensor_id", StringType(), nullable=False),
    StructField("sensor_type", StringType(), nullable=False),
    StructField("timestamp", StringType(), nullable=False),  # Will parse later
    StructField("reading_value", DoubleType(), nullable=True),
    StructField("unit", StringType(), nullable=True),
    StructField("status", StringType(), nullable=True),
    StructField("location", StringType(), nullable=True),
    StructField("battery_level", DoubleType(), nullable=True),
    StructField("signal_strength", IntegerType(), nullable=True),
])

print("\n📋 Expected Schema:")
for field in RAW_SENSOR_SCHEMA.fields:
    nullable = "NULL" if field.nullable else "NOT NULL"
    print(f"  • {field.name:20} {str(field.dataType):20} {nullable}")

# ==============================================================================
# DATA INGESTION
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 1: READ RAW DATA FROM SOURCE")
print("=" * 80)

try:
    # Read JSON files from source
    df_raw = spark.read \
        .option("multiLine", "true") \
        .json(f"{SOURCE_DATA_PATH}/*.json")
    
    record_count = df_raw.count()
    print(f"✅ Successfully read {record_count:,} records from source")
    print(f"✅ Columns found: {', '.join(df_raw.columns)}")
    
    # Show sample
    print("\n📊 Sample Raw Data:")
    df_raw.show(5, truncate=False)
    
except Exception as e:
    print(f"❌ Error reading source data: {str(e)}")
    raise

# ==============================================================================
# ADD BRONZE LAYER METADATA
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 2: ADD INGESTION METADATA")
print("=" * 80)

# Add metadata columns
df_bronze = df_raw \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_file", F.input_file_name()) \
    .withColumn("bronze_record_id", F.monotonically_increasing_id())

print("✅ Added metadata columns:")
print("  • ingestion_timestamp - When data was ingested")
print("  • ingestion_date - Date partition for efficiency")
print("  • source_file - Original file path for lineage")
print("  • bronze_record_id - Unique identifier in bronze layer")

# ==============================================================================
# BASIC DATA QUALITY CHECKS
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 3: BASIC QUALITY CHECKS (LOGGING ONLY)")
print("=" * 80)

# Check for nulls in critical fields
critical_fields = ["sensor_id", "sensor_type", "timestamp"]

for field in critical_fields:
    null_count = df_bronze.filter(F.col(field).isNull()).count()
    null_rate = (null_count / record_count) * 100 if record_count > 0 else 0
    
    if null_rate > 0:
        print(f"⚠️  {field}: {null_count:,} nulls ({null_rate:.2f}%)")
    else:
        print(f"✅ {field}: No nulls")

# Check for duplicates (log only, don't remove in Bronze)
duplicate_count = df_bronze.count() - df_bronze.dropDuplicates(
    ["sensor_id", "timestamp"]
).count()

if duplicate_count > 0:
    dup_rate = (duplicate_count / record_count) * 100
    print(f"⚠️  Found {duplicate_count:,} potential duplicates ({dup_rate:.2f}%)")
    print("   Note: Duplicates preserved in Bronze layer for audit purposes")
else:
    print(f"✅ No duplicates detected")

# ==============================================================================
# WRITE TO BRONZE DELTA TABLE
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 4: WRITE TO BRONZE DELTA TABLE")
print("=" * 80)

try:
    # Check if table exists
    from delta.tables import DeltaTable
    from pathlib import Path
    
    table_exists = Path(BRONZE_TABLE_PATH).exists() if config.RUN_MODE == "local" else False
    
    if table_exists:
        print(f"📊 Table exists - Appending new data")
        mode = "append"
    else:
        print(f"🆕 Creating new table")
        mode = "overwrite"
    
    # Write to Delta
    partition_cols = config.PROCESSING_CONFIG["partition_columns"]["bronze"]
    
    df_bronze.write \
        .format("delta") \
        .mode(mode) \
        .partitionBy(*partition_cols) \
        .option("overwriteSchema", "true") \
        .save(BRONZE_TABLE_PATH)
    
    print(f"✅ Successfully wrote {record_count:,} records to Bronze layer")
    print(f"✅ Partitioned by: {', '.join(partition_cols)}")
    print(f"✅ Location: {BRONZE_TABLE_PATH}")
    
except Exception as e:
    print(f"❌ Error writing to Bronze table: {str(e)}")
    raise

# ==============================================================================
# VERIFY WRITE
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 5: VERIFY DATA IN BRONZE TABLE")
print("=" * 80)

# Read back the data
df_verify = spark.read.format("delta").load(BRONZE_TABLE_PATH)

verify_count = df_verify.count()
print(f"✅ Verified: {verify_count:,} total records in Bronze table")

# Show partitions
print("\n📊 Partition Distribution:")
df_verify.groupBy("ingestion_date") \
    .agg(F.count("*").alias("record_count")) \
    .orderBy("ingestion_date") \
    .show()

# Sample of final data
print("\n📊 Sample Bronze Data:")
df_verify.select(
    "bronze_record_id",
    "sensor_id",
    "sensor_type",
    "timestamp",
    "reading_value",
    "ingestion_timestamp"
).show(10, truncate=False)

# ==============================================================================
# BRONZE LAYER STATISTICS
# ==============================================================================

print("\n" + "=" * 80)
print("BRONZE LAYER STATISTICS")
print("=" * 80)

stats = df_verify.select(
    F.count("*").alias("total_records"),
    F.countDistinct("sensor_id").alias("unique_sensors"),
    F.countDistinct("sensor_type").alias("sensor_types"),
    F.min("timestamp").alias("earliest_reading"),
    F.max("timestamp").alias("latest_reading"),
    F.countDistinct("ingestion_date").alias("ingestion_batches")
).collect()[0]

print(f"Total Records:     {stats['total_records']:,}")
print(f"Unique Sensors:    {stats['unique_sensors']:,}")
print(f"Sensor Types:      {stats['sensor_types']:,}")
print(f"Date Range:        {stats['earliest_reading']} to {stats['latest_reading']}")
print(f"Ingestion Batches: {stats['ingestion_batches']:,}")

# Sensor type distribution
print("\n📊 Sensor Type Distribution:")
df_verify.groupBy("sensor_type") \
    .agg(F.count("*").alias("count")) \
    .orderBy(F.desc("count")) \
    .show()

# ==============================================================================
# DELTA TABLE OPERATIONS
# ==============================================================================

print("\n" + "=" * 80)
print("DELTA TABLE OPERATIONS")
print("=" * 80)

# Show table history (if Delta table exists)
try:
    delta_table = DeltaTable.forPath(spark, BRONZE_TABLE_PATH)
    print("\n📜 Table History:")
    delta_table.history(5).select(
        "version", "timestamp", "operation", "operationMetrics"
    ).show(5, truncate=False)
except Exception as e:
    print(f"⚠️  Could not retrieve history: {str(e)}")

# ==============================================================================
# BRONZE LAYER SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("✅ BRONZE LAYER INGESTION COMPLETE")
print("=" * 80)

print(f"""
Bronze Layer Summary:
--------------------
✅ Raw data ingested with full fidelity
✅ Ingestion metadata added for lineage
✅ Data partitioned for efficient querying
✅ Stored in Delta format with ACID guarantees
✅ Ready for Silver layer processing

Next Step:
---------
→ Run Silver Layer notebook (02_silver_layer.py) to clean and validate data

Location: {BRONZE_TABLE_PATH}
Records:  {verify_count:,}
""")

print("=" * 80)

# Optional: Display execution time
# spark.stop()
