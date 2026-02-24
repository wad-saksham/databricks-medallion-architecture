"""
Configuration Management for Medallion Architecture Project

This module centralizes all configuration settings including:
- Storage paths (S3, local, DBFS)
- Databricks cluster settings
- Data quality thresholds
- Processing parameters
"""

import os
from pathlib import Path
from datetime import datetime

# ============================================================================
# ENVIRONMENT SETTINGS
# ============================================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")  # dev, staging, production
RUN_MODE = os.getenv("RUN_MODE", "local")  # local or databricks

# ============================================================================
# AWS CONFIGURATION
# ============================================================================

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "your-name-medallion-demo")

# S3 Paths - Medallion Layers
S3_BRONZE_PATH = f"s3a://{S3_BUCKET_NAME}/bronze"
S3_SILVER_PATH = f"s3a://{S3_BUCKET_NAME}/silver"
S3_GOLD_PATH = f"s3a://{S3_BUCKET_NAME}/gold"
S3_CHECKPOINT_PATH = f"s3a://{S3_BUCKET_NAME}/checkpoints"

# ============================================================================
# LOCAL CONFIGURATION (for testing)
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOCAL_DATA_DIR = PROJECT_ROOT / "data"
LOCAL_BRONZE_PATH = str(LOCAL_DATA_DIR / "bronze")
LOCAL_SILVER_PATH = str(LOCAL_DATA_DIR / "silver")
LOCAL_GOLD_PATH = str(LOCAL_DATA_DIR / "gold")
LOCAL_CHECKPOINT_PATH = str(LOCAL_DATA_DIR / "checkpoints")

# ============================================================================
# DATABRICKS CONFIGURATION
# ============================================================================

DBFS_MOUNT_POINT = "/mnt/medallion"
DBFS_BRONZE_PATH = f"{DBFS_MOUNT_POINT}/bronze"
DBFS_SILVER_PATH = f"{DBFS_MOUNT_POINT}/silver"
DBFS_GOLD_PATH = f"{DBFS_MOUNT_POINT}/gold"
DBFS_CHECKPOINT_PATH = f"{DBFS_MOUNT_POINT}/checkpoints"

# ============================================================================
# PATH RESOLUTION (based on run mode)
# ============================================================================

if RUN_MODE == "databricks":
    BRONZE_PATH = DBFS_BRONZE_PATH
    SILVER_PATH = DBFS_SILVER_PATH
    GOLD_PATH = DBFS_GOLD_PATH
    CHECKPOINT_PATH = DBFS_CHECKPOINT_PATH
elif RUN_MODE == "cloud":
    BRONZE_PATH = S3_BRONZE_PATH
    SILVER_PATH = S3_SILVER_PATH
    GOLD_PATH = S3_GOLD_PATH
    CHECKPOINT_PATH = S3_CHECKPOINT_PATH
else:  # local
    BRONZE_PATH = LOCAL_BRONZE_PATH
    SILVER_PATH = LOCAL_SILVER_PATH
    GOLD_PATH = LOCAL_GOLD_PATH
    CHECKPOINT_PATH = LOCAL_CHECKPOINT_PATH

# ============================================================================
# TABLE NAMES
# ============================================================================

# Bronze Tables
BRONZE_SENSOR_DATA = "sensor_data_raw"

# Silver Tables  
SILVER_SENSOR_DATA = "sensor_data_clean"

# Gold Tables
GOLD_SENSOR_METRICS_DAILY = "sensor_metrics_daily"
GOLD_SENSOR_METRICS_HOURLY = "sensor_metrics_hourly"
GOLD_ANOMALY_DETECTION = "sensor_anomalies"

# ============================================================================
# SPARK CONFIGURATION
# ============================================================================

SPARK_CONFIG = {
    "spark.app.name": "MedallionArchitecture",
    "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
    "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.databricks.delta.optimizeWrite.enabled": "true",
    "spark.databricks.delta.autoCompact.enabled": "true",
}

# For local development with less memory
if RUN_MODE == "local":
    SPARK_CONFIG.update({
        "spark.driver.memory": "4g",
        "spark.executor.memory": "4g",
        "spark.sql.shuffle.partitions": "4",
    })

# ============================================================================
# DATA QUALITY THRESHOLDS
# ============================================================================

QUALITY_THRESHOLDS = {
    # Null rate thresholds (max percentage allowed)
    "null_rate": {
        "sensor_id": 0.0,      # No nulls allowed
        "timestamp": 0.0,      # No nulls allowed
        "reading_value": 0.05, # Max 5% nulls
        "sensor_type": 0.0,    # No nulls allowed
        "location": 0.1,       # Max 10% nulls
    },
    
    # Duplicate thresholds
    "duplicates": {
        "max_duplicate_rate": 0.01,  # Max 1% duplicates
    },
    
    # Value ranges
    "value_ranges": {
        "temperature": {"min": -50, "max": 150},
        "pressure": {"min": 0, "max": 1000},
        "humidity": {"min": 0, "max": 100},
        "vibration": {"min": 0, "max": 500},
    },
    
    # Freshness (max age in hours)
    "data_freshness": {
        "max_age_hours": 24,
    },
    
    # Schema validation
    "schema": {
        "enforce_schema": True,
        "allow_schema_evolution": False,
    }
}

# ============================================================================
# PROCESSING CONFIGURATION
# ============================================================================

PROCESSING_CONFIG = {
    # Batch sizes
    "batch_size": 10000,
    "max_records_per_file": 100000,
    
    # Partitioning
    "partition_columns": {
        "bronze": ["ingestion_date"],
        "silver": ["date", "sensor_type"],
        "gold": ["date"],
    },
    
    # Optimization
    "z_order_columns": {
        "silver": ["sensor_id", "timestamp"],
        "gold": ["sensor_type"],
    },
    
    # Retention
    "retention_days": {
        "bronze": 90,   # Keep raw data for 90 days
        "silver": 365,  # Keep clean data for 1 year
        "gold": 730,    # Keep aggregates for 2 years
    },
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# METADATA
# ============================================================================

PROJECT_NAME = "Medallion Architecture - IoT Sensors"
PROJECT_VERSION = "1.0.0"
AUTHOR = "Your Name"
CREATED_DATE = "2024-02-18"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_bronze_path(table_name: str) -> str:
    """Get full path to bronze table"""
    return f"{BRONZE_PATH}/{table_name}"

def get_silver_path(table_name: str) -> str:
    """Get full path to silver table"""
    return f"{SILVER_PATH}/{table_name}"

def get_gold_path(table_name: str) -> str:
    """Get full path to gold table"""
    return f"{GOLD_PATH}/{table_name}"

def get_checkpoint_path(table_name: str) -> str:
    """Get checkpoint path for streaming/incremental processing"""
    return f"{CHECKPOINT_PATH}/{table_name}"

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def print_config():
    """Print current configuration (for debugging)"""
    print(f"=" * 70)
    print(f"CONFIGURATION - {ENVIRONMENT.upper()} Environment")
    print(f"=" * 70)
    print(f"Run Mode: {RUN_MODE}")
    print(f"Bronze Path: {BRONZE_PATH}")
    print(f"Silver Path: {SILVER_PATH}")
    print(f"Gold Path: {GOLD_PATH}")
    print(f"AWS Region: {AWS_REGION}")
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print(f"=" * 70)

# ============================================================================
# SAMPLE DATA GENERATION CONFIG
# ============================================================================

SAMPLE_DATA_CONFIG = {
    "num_sensors": 50,
    "num_records": 10000,
    "sensor_types": ["temperature", "pressure", "humidity", "vibration"],
    "locations": ["Factory_A", "Factory_B", "Factory_C", "Warehouse_1", "Warehouse_2"],
    "start_date": "2024-01-01",
    "end_date": "2024-02-18",
    "anomaly_rate": 0.02,  # 2% anomalous readings
}

if __name__ == "__main__":
    print_config()
