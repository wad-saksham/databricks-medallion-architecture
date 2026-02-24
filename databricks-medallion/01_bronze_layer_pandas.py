"""
BRONZE LAYER - PANDAS VERSION (Windows Compatible)

This is a pandas-based alternative to the PySpark bronze layer.
Use this for local development on Windows where PySpark may have compatibility issues.

Purpose:
    - Ingest raw JSON data from sample directory
    - Add metadata (ingestion timestamp, source file)
    - Store in Parquet format with partitioning
    - Basic data quality checks
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("BRONZE LAYER - RAW DATA INGESTION (Pandas Version)")
print("=" * 80)

# Configuration
PROJECT_ROOT = Path(__file__).parent
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"

# Create bronze directory
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n📁 Source: {SAMPLE_DIR}")
print(f"📁 Target: {BRONZE_DIR}\n")

# Find all JSON files
json_files = list(SAMPLE_DIR.glob("*.json"))
print(f"Found {len(json_files)} JSON files to process\n")

if not json_files:
    print("❌ No JSON files found. Run generate_sample_data.py first!")
    exit(1)

# Process each file
all_records = []
total_records = 0

for json_file in sorted(json_files):
    print(f"Processing: {json_file.name}...", end=" ")
    
    # Read JSON lines
    with open(json_file, 'r') as f:
        batch_records = [json.loads(line) for line in f]
    
    # Add metadata
    ingestion_time = datetime.now()
    for record in batch_records:
        record['ingestion_timestamp'] = ingestion_time
        record['source_file'] = json_file.name
    
    all_records.extend(batch_records)
    total_records += len(batch_records)
    print(f"✅ {len(batch_records):,} records")

# Create DataFrame
print(f"\nCreating DataFrame with {total_records:,} total records...")
df = pd.DataFrame(all_records)

# Data Quality Checks
print("\n" + "=" * 80)
print("DATA QUALITY CHECKS")
print("=" * 80)

print(f"\n📊 Total Records: {len(df):,}")
print(f"📊 Total Columns: {len(df.columns)}")
print(f"📊 Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Check for nulls
print("\n🔍 Null Value Analysis:")
null_counts = df.isnull().sum()
null_counts = null_counts[null_counts > 0]
if len(null_counts) > 0:
    for col, count in null_counts.items():
        pct = (count / len(df)) * 100
        print(f"  ⚠️  {col}: {count:,} nulls ({pct:.2f}%)")
else:
    print("  ✅ No null values found")

# Check for duplicates
duplicates = df.duplicated().sum()
print(f"\n📋 Duplicate Records: {duplicates:,}")

# Value range checks
print("\n📈 Reading Value Statistics:")
reading_stats = df.groupby('sensor_type')['reading_value'].agg(['count', 'mean', 'min', 'max', 'std'])
print(reading_stats.round(2))

# Partition by ingestion date
print("\n" + "=" * 80)
print("WRITING TO BRONZE LAYER")
print("=" * 80)

df['ingestion_date'] = pd.to_datetime(df['ingestion_timestamp']).dt.date

# Write partitioned parquet
print(f"\nWriting partitioned Parquet files...")
output_file = BRONZE_DIR / "sensors_bronze.parquet"

df.to_parquet(
    output_file,
    engine='pyarrow',
    compression='snappy',
    index=False,
    partition_cols=['ingestion_date']
)

print(f"✅ Data written to: {output_file}")

# Verify the write
print("\n🔍 Verifying written data...")
df_verify = pd.read_parquet(output_file)
print(f"✅ Verified: {len(df_verify):,} records read back")

# Display sample
print("\n" + "=" * 80)
print("SAMPLE BRONZE LAYER DATA (first 5 rows)")
print("=" * 80)
print(df_verify.head())

# Summary statistics
print("\n" + "=" * 80)
print("BRONZE LAYER SUMMARY")
print("=" * 80)
print(f"✅ Total Records Ingested: {len(df):,}")
print(f"✅ Files Processed: {len(json_files)}")
print(f"✅ Unique Devices: {df['device_id'].nunique()}")
print(f"✅ Unique Locations: {df['location'].nunique()}")
print(f"✅ Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"✅ Output: {BRONZE_DIR}")
print("=" * 80)

print("\n✅ BRONZE LAYER INGESTION COMPLETE!")
print("\nNext step: Run 02_silver_layer_pandas.py to clean and validate the  data")
