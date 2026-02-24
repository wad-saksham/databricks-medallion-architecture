"""
GOLD LAYER - Business Aggregations

Purpose:
    Create business-ready, aggregated datasets from Silver layer for analytics and BI.
    Optimize for query performance and business user consumption.
    
Gold Layer Principles:
    - Denormalized for performance
    - Pre-aggregated metrics
    - Business-friendly column names
    - Optimized for specific use cases
    - Supports dashboards and reports

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
from delta.tables import DeltaTable

from src.config import config
from src.utils import spark_utils

# ==============================================================================
# CONFIGURATION
# ==============================================================================

print("=" * 80)
print("GOLD LAYER - BUSINESS AGGREGATIONS")
print("=" * 80)

# Create Spark Session
spark = spark_utils.create_spark_session(
    app_name="Gold_Layer_Aggregations",
    config=config.SPARK_CONFIG
)

# Paths
SILVER_TABLE_PATH = config.get_silver_path(config.SILVER_SENSOR_DATA)
GOLD_DAILY_PATH = config.get_gold_path(config.GOLD_SENSOR_METRICS_DAILY)
GOLD_HOURLY_PATH = config.get_gold_path(config.GOLD_SENSOR_METRICS_HOURLY)
GOLD_ANOMALY_PATH = config.get_gold_path(config.GOLD_ANOMALY_DETECTION)

print(f"\n📂 Silver Source: {SILVER_TABLE_PATH}")
print(f"📂 Gold Daily Metrics: {GOLD_DAILY_PATH}")
print(f"📂 Gold Hourly Metrics: {GOLD_HOURLY_PATH}")
print(f"📂 Gold Anomaly Detection: {GOLD_ANOMALY_PATH}")

# ==============================================================================
# READ SILVER DATA
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 1: READ CLEAN DATA FROM SILVER LAYER")
print("=" * 80)

try:
    df_silver = spark.read.format("delta").load(SILVER_TABLE_PATH)
    silver_count = df_silver.count()
    print(f"✅ Read {silver_count:,} records from Silver layer")
    
    # Filter out poor quality data for Gold layer
    df_silver_quality = df_silver.filter(F.col("quality_score") >= 50)
    quality_count = df_silver_quality.count()
    filtered_count = silver_count - quality_count
    
    print(f"✅ Using {quality_count:,} high-quality records (≥50 quality score)")
    print(f"   Filtered out {filtered_count:,} low-quality records")
    
except Exception as e:
    print(f"❌ Error reading Silver data: {str(e)}")
    raise

# ==============================================================================
# GOLD TABLE 1: DAILY SENSOR METRICS
# ==============================================================================

print("\n" + "=" * 80)
print("GOLD TABLE 1: DAILY SENSOR METRICS")
print("=" * 80)

print("\n📊 Creating daily aggregated metrics by sensor...")

df_gold_daily = df_silver_quality.groupBy(
    "date",
    "sensor_id",
    "sensor_type",
    "location"
).agg(
    # Reading statistics
    F.count("reading_value").alias("total_readings"),
    F.avg("reading_value").alias("avg_reading"),
    F.min("reading_value").alias("min_reading"),
    F.max("reading_value").alias("max_reading"),
    F.stddev("reading_value").alias("std_reading"),
    
    # Data quality metrics
    F.avg("quality_score").alias("avg_quality_score"),
    F.sum(F.when(F.col("is_anomaly") == True, 1).otherwise(0)).alias("anomaly_count"),
    F.sum(F.when(F.col("reading_value").isNull(), 1).otherwise(0)).alias("null_readings"),
    
    # Sensor health
    F.avg("battery_level").alias("avg_battery_level"),
    F.min("battery_level").alias("min_battery_level"),
    F.avg("signal_strength").alias("avg_signal_strength"),
    
    # Operational metrics
    F.min("timestamp").alias("first_reading_timestamp"),
    F.max("timestamp").alias("last_reading_timestamp"),
    F.count("*").alias("raw_record_count")
)

# Add derived business metrics
df_gold_daily = df_gold_daily.withColumn(
    "data_quality_pct",
    (F.col("total_readings") - F.col("null_readings")) / F.col("total_readings") * 100
).withColumn(
    "anomaly_rate_pct",
    F.col("anomaly_count") / F.col("total_readings") * 100
).withColumn(
    "reading_range",
    F.col("max_reading") - F.col("min_reading")
).withColumn(
    "sensor_health_score",
    F.when(
        (F.col("avg_battery_level") > 50) & 
        (F.col("avg_signal_strength") >= 3),
        F.lit("HEALTHY")
    ).when(
        (F.col("avg_battery_level") > 20) & 
        (F.col("avg_signal_strength") >= 2),
        F.lit("WARNING")
    ).otherwise(F.lit("CRITICAL"))
).withColumn(
    "gold_processing_timestamp",
    F.current_timestamp()
)

# Add date partitions
df_gold_daily = df_gold_daily \
    .withColumn("year", F.year("date")) \
    .withColumn("month", F.month("date"))

daily_count = df_gold_daily.count()
print(f"✅ Created {daily_count:,} daily aggregation records")

# Show sample
print("\n📊 Sample Daily Metrics:")
df_gold_daily.select(
    "date", "sensor_id", "sensor_type", 
    "total_readings", "avg_reading", "anomaly_count", "sensor_health_score"
).show(10, truncate=False)

# Write to Delta
print(f"\n💾 Writing to {GOLD_DAILY_PATH}")
df_gold_daily.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("date") \
    .option("overwriteSchema", "true") \
    .save(GOLD_DAILY_PATH)

print(f"✅ Daily metrics table created successfully")

# ==============================================================================
# GOLD TABLE 2: HOURLY SENSOR METRICS
# ==============================================================================

print("\n" + "=" * 80)
print("GOLD TABLE 2: HOURLY SENSOR METRICS")
print("=" * 80)

print("\n📊 Creating hourly aggregated metrics...")

df_gold_hourly = df_silver_quality.groupBy(
    "date",
    "hour",
    "sensor_type",
    "location"
).agg(
    # Reading statistics
    F.count("reading_value").alias("total_readings"),
    F.avg("reading_value").alias("avg_reading"),
    F.min("reading_value").alias("min_reading"),
    F.max("reading_value").alias("max_reading"),
    
    # Unique sensors
    F.countDistinct("sensor_id").alias("active_sensors"),
    
    # Quality metrics
    F.avg("quality_score").alias("avg_quality_score"),
    F.sum(F.when(F.col("is_anomaly") == True, 1).otherwise(0)).alias("anomaly_count"),
    
    # System health
    F.avg("battery_level").alias("avg_battery_level"),
    F.avg("signal_strength").alias("avg_signal_strength")
)

# Add business metrics
df_gold_hourly = df_gold_hourly.withColumn(
    "anomaly_rate_pct",
    (F.col("anomaly_count") / F.col("total_readings") * 100).cast("decimal(5,2)")
).withColumn(
    "hour_of_day",
    F.col("hour")
).withColumn(
    "datetime",
    F.concat(F.col("date").cast("string"), F.lit(" "), F.col("hour").cast("string"), F.lit(":00:00"))
).withColumn(
    "gold_processing_timestamp",
    F.current_timestamp()
)

hourly_count = df_gold_hourly.count()
print(f"✅ Created {hourly_count:,} hourly aggregation records")

# Show sample
print("\n📊 Sample Hourly Metrics:")
df_gold_hourly.select(
    "date", "hour", "sensor_type", "location",
    "total_readings", "avg_reading", "active_sensors"
).show(10, truncate=False)

# Write to Delta
print(f"\n💾 Writing to {GOLD_HOURLY_PATH}")
df_gold_hourly.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("date") \
    .option("overwriteSchema", "true") \
    .save(GOLD_HOURLY_PATH)

print(f"✅ Hourly metrics table created successfully")

# ==============================================================================
# GOLD TABLE 3: ANOMALY DETECTION & ALERTS
# ==============================================================================

print("\n" + "=" * 80)
print("GOLD TABLE 3: ANOMALY DETECTION & ALERTS")
print("=" * 80)

print("\n📊 Creating anomaly detection dataset...")

# Filter only anomalous readings
df_anomalies = df_silver.filter(F.col("is_anomaly") == True)

# Add severity classification
df_gold_anomalies = df_anomalies.withColumn(
    "severity",
    F.when(F.col("quality_score") < 25, F.lit("CRITICAL"))
     .when(F.col("quality_score") < 50, F.lit("HIGH"))
     .when(F.col("quality_score") < 75, F.lit("MEDIUM"))
     .otherwise(F.lit("LOW"))
)

# Add expected ranges based on sensor type
df_gold_anomalies = df_gold_anomalies.withColumn(
    "expected_min",
    F.when(F.col("sensor_type") == "temperature", F.lit(-50.0))
     .when(F.col("sensor_type") == "pressure", F.lit(0.0))
     .when(F.col("sensor_type") == "humidity", F.lit(0.0))
     .when(F.col("sensor_type") == "vibration", F.lit(0.0))
     .otherwise(F.lit(0.0))
).withColumn(
    "expected_max",
    F.when(F.col("sensor_type") == "temperature", F.lit(150.0))
     .when(F.col("sensor_type") == "pressure", F.lit(1000.0))
     .when(F.col("sensor_type") == "humidity", F.lit(100.0))
     .when(F.col("sensor_type") == "vibration", F.lit(500.0))
     .otherwise(F.lit(1000.0))
)

# Calculate deviation
df_gold_anomalies = df_gold_anomalies.withColumn(
    "deviation_type",
    F.when(F.col("reading_value") < F.col("expected_min"), F.lit("BELOW_THRESHOLD"))
     .when(F.col("reading_value") > F.col("expected_max"), F.lit("ABOVE_THRESHOLD"))
     .otherwise(F.lit("UNKNOWN"))
).withColumn(
    "deviation_amount",
    F.when(
        F.col("reading_value") < F.col("expected_min"),
        F.col("expected_min") - F.col("reading_value")
    ).when(
        F.col("reading_value") > F.col("expected_max"),
        F.col("reading_value") - F.col("expected_max")
    ).otherwise(F.lit(0.0))
)

# Select final columns
df_gold_anomalies = df_gold_anomalies.select(
    "silver_record_id",
    "sensor_id",
    "sensor_type",
    "timestamp",
    "date",
    "location",
    "reading_value",
    "expected_min",
    "expected_max",
    "deviation_type",
    "deviation_amount",
    "severity",
    "status",
    "battery_level",
    "signal_strength",
    "quality_score",
    "gold_processing_timestamp"
).withColumn(
    "alert_message",
    F.concat(
        F.lit("Anomaly detected on sensor "),
        F.col("sensor_id"),
        F.lit(" ("),
        F.col("sensor_type"),
        F.lit("): "),
        F.col("deviation_type"),
        F.lit(" by "),
        F.round("deviation_amount", 2),
        F.lit(" units")
    )
)

anomaly_count = df_gold_anomalies.count()
print(f"✅ Created {anomaly_count:,} anomaly records")

if anomaly_count > 0:
    # Show sample
    print("\n📊 Sample Anomalies:")
    df_gold_anomalies.select(
        "sensor_id", "timestamp", "sensor_type",
        "reading_value", "deviation_type", "severity"
    ).show(10, truncate=False)
    
    # Anomaly statistics
    print("\n📊 Anomaly Distribution:")
    df_gold_anomalies.groupBy("sensor_type", "severity") \
        .agg(F.count("*").alias("count")) \
        .orderBy("sensor_type", "severity") \
        .show()
    
    # Write to Delta
    print(f"\n💾 Writing to {GOLD_ANOMALY_PATH}")
    df_gold_anomalies.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy("date") \
        .option("overwriteSchema", "true") \
        .save(GOLD_ANOMALY_PATH)
    
    print(f"✅ Anomaly detection table created successfully")
else:
    print("ℹ️  No anomalies detected in the dataset")

# ==============================================================================
# BUSINESS INSIGHTS & ANALYTICS
# ==============================================================================

print("\n" + "=" * 80)
print("BUSINESS INSIGHTS & KEY METRICS")
print("=" * 80)

# Read back gold tables for analysis
df_daily = spark.read.format("delta").load(GOLD_DAILY_PATH)

# Overall Statistics
print("\n📊 Overall System Health:")

overall_stats = df_daily.agg(
    F.countDistinct("sensor_id").alias("total_sensors"),
    F.avg("avg_reading").alias("system_avg_reading"),
    F.avg("avg_quality_score").alias("system_quality_score"),
    F.sum("anomaly_count").alias("total_anomalies"),
    F.avg("avg_battery_level").alias("avg_battery_level")
).collect()[0]

print(f"""
Total Active Sensors:      {overall_stats['total_sensors']}
System Avg Reading:        {overall_stats['system_avg_reading']:.2f}
System Quality Score:      {overall_stats['system_quality_score']:.1f}/100
Total Anomalies:           {overall_stats['total_anomalies']}
Avg Battery Level:         {overall_stats['avg_battery_level']:.1f}%
""")

# Sensor Health Distribution
print("\n📊 Sensor Health Distribution:")
df_daily.groupBy("sensor_health_score") \
    .agg(F.countDistinct("sensor_id").alias("sensor_count")) \
    .orderBy("sensor_health_score") \
    .show()

# Top 10 Most Active Sensors
print("\n📊 Top 10 Most Active Sensors:")
df_daily.groupBy("sensor_id", "sensor_type") \
    .agg(
        F.sum("total_readings").alias("total_readings"),
        F.avg("avg_quality_score").alias("avg_quality")
    ) \
    .orderBy(F.desc("total_readings")) \
    .limit(10) \
    .show(truncate=False)

# Location Analysis
print("\n📊 Performance by Location:")
df_daily.groupBy("location") \
    .agg(
        F.countDistinct("sensor_id").alias("sensors"),
        F.sum("total_readings").alias("readings"),
        F.avg("avg_quality_score").alias("avg_quality"),
        F.sum("anomaly_count").alias("anomalies")
    ) \
    .orderBy(F.desc("readings")) \
    .show(truncate=False)

# Sensor Type Performance
print("\n📊 Performance by Sensor Type:")
df_daily.groupBy("sensor_type") \
    .agg(
        F.countDistinct("sensor_id").alias("sensors"),
        F.avg("avg_reading").alias("avg_value"),
        F.avg("avg_quality_score").alias("avg_quality"),
        F.sum("anomaly_count").alias("total_anomalies")
    ) \
    .orderBy("sensor_type") \
    .show(truncate=False)

# ==============================================================================
# OPTIMIZE GOLD TABLES
# ==============================================================================

print("\n" + "=" * 80)
print("OPTIMIZING GOLD TABLES")
print("=" * 80)

for table_name, table_path in [
    ("Daily Metrics", GOLD_DAILY_PATH),
    ("Hourly Metrics", GOLD_HOURLY_PATH),
    ("Anomaly Detection", GOLD_ANOMALY_PATH)
]:
    try:
        print(f"\n🔧 Optimizing {table_name}...")
        spark.sql(f"OPTIMIZE delta.`{table_path}`")
        print(f"✅ {table_name} optimized")
    except Exception as e:
        print(f"⚠️  Could not optimize {table_name}: {str(e)}")

# ==============================================================================
# SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("✅ GOLD LAYER PROCESSING COMPLETE")
print("=" * 80)

print(f"""
Gold Layer Summary:
------------------
✅ Created 3 business-ready datasets:
   1. Daily Sensor Metrics ({daily_count:,} records)
   2. Hourly Time-Series Metrics ({hourly_count:,} records)
   3. Anomaly Detection & Alerts ({anomaly_count:,} records)

✅ Data optimized for analytics workloads
✅ Business metrics calculated
✅ Ready for BI tools and dashboards

Key Business Metrics:
--------------------
Active Sensors:         {overall_stats['total_sensors']}
System Quality:         {overall_stats['system_quality_score']:.1f}/100
Total Anomalies:        {overall_stats['total_anomalies']}
Avg Battery Level:      {overall_stats['avg_battery_level']:.1f}%

Use Cases Supported:
-------------------
📊 Performance Dashboards
📈 Trend Analysis  
🚨 Anomaly Alerts
🔋 Sensor Health Monitoring
📍 Location-based Analytics
⏰ Time-series Forecasting

Next Steps:
----------
1. Connect to Power BI or Tableau for visualization
2. Set up automated alerts for anomalies
3. Export data for ML model training
4. Schedule daily/hourly refresh jobs

Gold Table Locations:
--------------------
Daily Metrics:    {GOLD_DAILY_PATH}
Hourly Metrics:   {GOLD_HOURLY_PATH}
Anomaly Alerts:   {GOLD_ANOMALY_PATH}
""")

print("=" * 80)
print("🎉 MEDALLION ARCHITECTURE IMPLEMENTATION COMPLETE!")
print("=" * 80)

# spark.stop()
