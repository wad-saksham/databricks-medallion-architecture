"""
ENVIRONMENT SETUP AND CONFIGURATION

This notebook sets up the environment and generates sample data for the Medallion Architecture project.
Run this FIRST before running any other notebooks.

Purpose:
    - Verify Spark installation
    - Generate sample IoT sensor data
   - Configure AWS/cloud connections (optional)
    - Create necessary directories
    - Test basic operations

Author: Your Name
Date: 2024-02-18
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import sys
from pathlib import Path

print("=" * 80)
print("MEDALLION ARCHITECTURE - ENVIRONMENT SETUP")
print("=" * 80)

# Add src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

print(f"\n📁 Project Root: {project_root}")

# ==============================================================================
# STEP 1: VERIFY PYTHON ENVIRONMENT
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 1: VERIFY PYTHON ENVIRONMENT")
print("=" * 80)

import platform
print(f"✅ Python Version: {sys.version}")
print(f"✅ Platform: {platform.system()} {platform.release()}")

# Warn about Python 3.13 compatibility
if sys.version_info >= (3, 13):
    print("\n⚠️  WARNING: Python 3.13 has limited PySpark compatibility.")
    print("   If you encounter issues, consider using Python 3.11 or 3.12")
    print("   Download from: https://www.python.org/downloads/")

# Check required packages
required_packages = [
    "pyspark",
    "delta",
    "pandas",
    "faker",
]

print("\n📦 Checking required packages:")
for package in required_packages:
    try:
        module = __import__(package.replace("-", "_"))
        version = getattr(module, "__version__", "unknown")
        print(f"  ✅ {package:20} version {version}")
    except ImportError:
        print(f"  ❌ {package:20} NOT INSTALLED")
        print(f"     Run: pip install {package}")

# ==============================================================================
# STEP 2: VERIFY SPARK INSTALLATION
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 2: VERIFY SPARK INSTALLATION")
print("=" * 80)

try:
    from pyspark.sql import SparkSession
    from src.utils import spark_utils
    from src.config import config
    
    # Create Spark session
    spark = spark_utils.create_spark_session(
        app_name="Environment_Setup_Test",
        config=config.SPARK_CONFIG
    )
    
    print(f"✅ Spark Session Created")
    print(f"✅ Spark Version: {spark.version}")
    print(f"✅ Spark Master: {spark.sparkContext.master}")
    
    # Test basic Spark operation
    test_df = spark.createDataFrame([(1, "test"), (2, "data")], ["id", "value"])
    count = test_df.count()
    
    print(f"✅ Basic Spark Test: Created DataFrame with {count} rows")
    test_df.show()
    
except Exception as e:
    print(f"❌ Spark Setup Error: {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Make sure Java 11+ is installed")
    print("  2. Set JAVA_HOME environment variable")
    print("  3. Reinstall pyspark: pip install pyspark==3.5.0")
    sys.exit(1)

# ==============================================================================
# STEP 3: VERIFY DELTA LAKE
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 3: VERIFY DELTA LAKE")
print("=" * 80)

try:
    from delta import DeltaTable
    
    # Test Delta write/read
    test_delta_path = str(project_root / "data" / "test_delta")
    
    test_df.write.format("delta").mode("overwrite").save(test_delta_path)
    print(f"✅ Delta Write Test: Wrote to {test_delta_path}")
    
    df_read = spark.read.format("delta").load(test_delta_path)
    print(f"✅ Delta Read Test: Read {df_read.count()} rows")
    
    # Cleanup test data
    import shutil
    if Path(test_delta_path).exists():
        shutil.rmtree(test_delta_path)
        print(f"✅ Cleanup: Removed test Delta table")
    
except Exception as e:
    print(f"❌ Delta Lake Error: {str(e)}")
    print("  Make sure delta-spark is installed: pip install delta-spark")
    sys.exit(1)

# ==============================================================================
# STEP 4: CREATE PROJECT DIRECTORIES
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 4: CREATE PROJECT DIRECTORIES")
print("=" * 80)

# Create necessary directories
directories = [
    project_root / "data" / "sample" / "historical",
    project_root / "data" / "sample" / "streaming",
    project_root / "data" / "sample" / "test",
    project_root / "data" / "bronze",
    project_root / "data" / "silver",
    project_root / "data" / "gold",
    project_root / "data" / "checkpoints",
]

print("\n📁 Creating directories:")
for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ {directory.relative_to(project_root)}")

print(f"\n✅ All directories created successfully")

# ==============================================================================
# STEP 5: GENERATE SAMPLE DATA
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 5: GENERATE SAMPLE IOT SENSOR DATA")
print("=" * 80)

try:
    from src.utils.data_generator import IoTDataGenerator
    from datetime import datetime, timedelta
    
    print("\n🔄 Initializing data generator...")
    generator = IoTDataGenerator(seed=42)
    
    # Generate historical data (7 days)
    print("\n📊 Generating historical data (7 days)...")
    start_date = datetime(2024, 2, 1)
    end_date = datetime(2024, 2, 7)
    
    historical_data = generator.generate_batch(
        start_date=start_date,
        end_date=end_date,
        records_per_day=20,  # 20 readings per day per sensor
        anomaly_rate=0.02    # 2% anomalies
    )
    
    # Save to JSON files
    output_dir = project_root / "data" / "sample" / "historical"
    generator.save_to_json(
        historical_data,
        str(output_dir),
        split_files=3  # Split into 3 files
    )
    
    print(f"✅ Generated {len(historical_data):,} historical records")
    print(f"✅ Saved to: {output_dir}")
    
    # Generate streaming data (1 hour)
    print("\n📊 Generating streaming data (recent 1 hour)...")
    streaming_data = generator.generate_streaming_data(
        duration_seconds=3600,  # 1 hour
        rate_per_second=2
    )
    
    output_dir = project_root / "data" / "sample" / "streaming"
    generator.save_to_json(
        streaming_data,
        str(output_dir),
        split_files=1
    )
    
    print(f"✅ Generated {len(streaming_data):,} streaming records")
    print(f"✅ Saved to: {output_dir}")
    
    # Generate small test set
    print("\n📊 Generating test data (1 day)...")
    test_data = generator.generate_batch(
        start_date=datetime(2024, 2, 18),
        end_date=datetime(2024, 2, 18),
        records_per_day=10,
        anomaly_rate=0.05
    )
    
    output_dir = project_root / "data" / "sample" / "test"
    generator.save_to_json(test_data, str(output_dir), split_files=1)
    generator.save_to_csv(
        test_data[:500],  # Save first 500 as CSV
        str(output_dir / "sensor_data_sample.csv")
    )
    
    print(f"✅ Generated {len(test_data):,} test records")
    print(f"✅ Saved to: {output_dir}")
    
except Exception as e:
    print(f"❌ Data Generation Error: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\nContinuing setup...")

# ==============================================================================
# STEP 6: DISPLAY CONFIGURATION
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 6: DISPLAY CONFIGURATION")
print("=" * 80)

config.print_config()

print("\n📋 Key Paths:")
print(f"  Bronze Layer: {config.BRONZE_PATH}")
print(f"  Silver Layer: {config.SILVER_PATH}")
print(f"  Gold Layer:   {config.GOLD_PATH}")

# ==============================================================================
# STEP 7: TEST DATA PREVIEW
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 7: PREVIEW SAMPLE DATA")
print("=" * 80)

try:
    # Read one of the generated JSON files
    sample_file = project_root / "data" / "sample" / "test" / "sensor_data.json"
    
    if sample_file.exists():
        df_sample = spark.read.option("multiLine", "true").json(str(sample_file).replace("\\", "/"))
        
        print(f"\n📊 Sample Data from: {sample_file.name}")
        print(f"   Total Records: {df_sample.count():,}")
        print(f"   Columns: {', '.join(df_sample.columns)}")
        
        print("\n📋 Data Schema:")
        df_sample.printSchema()
        
        print("\n📊 Sample Records:")
        df_sample.select(
            "sensor_id", "sensor_type", "timestamp",
            "reading_value", "status", "location"
        ).show(10, truncate=False)
        
        # Statistics by sensor type
        print("\n📊 Data Summary by Sensor Type:")
        df_sample.groupBy("sensor_type") \
            .agg(
                {"reading_value": "count", "reading_value": "avg"}
            ) \
            .show()
    else:
        print(f"⚠️  Sample file not found: {sample_file}")
        
except Exception as e:
    print(f"⚠️  Could not preview data: {str(e)}")

# ==============================================================================
# STEP 8: VERIFY AWS/CLOUD SETUP (OPTIONAL)
# ==============================================================================

print("\n" + "=" * 80)
print("STEP 8: VERIFY CLOUD SETUP (OPTIONAL)")
print("=" * 80)

print("\n📋 AWS Configuration:")
import os
if os.getenv("AWS_ACCESS_KEY_ID"):
    print("  ✅ AWS credentials found in environment")
    print(f"  ✅ S3 Bucket: {config.S3_BUCKET_NAME}")
    print(f"  ✅ AWS Region: {config.AWS_REGION}")
    
    # Try to list S3 bucket (optional)
    try:
        import boto3
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=config.S3_BUCKET_NAME, MaxKeys=1)
        print(f"  ✅ S3 connection successful")
    except Exception as e:
        print(f"  ⚠️  Could not connect to S3: {str(e)}")
        print(f"     You can still run locally without S3")
else:
    print("  ℹ️  No AWS credentials found (running in local mode)")
    print("     To enable S3, run: aws configure")

# ==============================================================================
# SUMMARY AND NEXT STEPS
# ==============================================================================

print("\n" + "=" * 80)
print("✅ ENVIRONMENT SETUP COMPLETE!")
print("=" * 80)

print(f"""
Setup Summary:
-------------
✅ Python environment verified
✅ PySpark and Delta Lake configured
✅ Project directories created
✅ Sample data generated
✅ Configuration loaded

Sample Data Generated:
---------------------
📊 Historical data:  {len(historical_data):,} records (7 days)
📊 Streaming data:   {len(streaming_data):,} records (1 hour)
📊 Test data:        {len(test_data):,} records (1 day)

Next Steps:
----------
1. Run Bronze Layer:  notebooks/01_bronze_layer.py
2. Run Silver Layer:  notebooks/02_silver_layer.py
3. Run Gold Layer:    notebooks/03_gold_layer.py

Run Mode: {config.RUN_MODE}
Environment: {config.ENVIRONMENT}

To run the full pipeline locally:
---------------------------------
cd "{project_root}"
python notebooks/01_bronze_layer.py
python notebooks/02_silver_layer.py
python notebooks/03_gold_layer.py

For Databricks:
--------------
1. Upload notebooks to Databricks workspace
2. Upload src/ folder to workspace
3. Create cluster (Runtime 13.3 LTS or higher)
4. Run notebooks in sequence

📚 Documentation:
----------------
- README.md - Project overview
- LEARNING_GUIDE.md - Concepts explained
- MASTER_ROADMAP.md - Complete project plan
""")

print("=" * 80)
print("🚀 Ready to start building! Good luck!")
print("=" * 80)

spark.stop()
