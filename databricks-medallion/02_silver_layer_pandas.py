"""
SILVER LAYER - PANDAS VERSION (Windows Compatible)

Clean and validate data from Bronze layer.

Purpose:
    - Remove duplicates
    - Handle null values
    - Validate data quality rules
    - Standardize formats
    - Add data quality flags
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SILVER LAYER - DATA CLEANING & VALIDATION (Pandas Version)")
print("=" * 80)

# Configuration
PROJECT_ROOT = Path(__file__).parent
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"

# Create silver directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n📁 Source: {BRONZE_DIR}")
print(f"📁 Target: {SILVER_DIR}\n")

# Read Bronze data
print("Reading Bronze layer data...")
bronze_file = BRONZE_DIR / "sensors_bronze.parquet"

if not bronze_file.exists():
    print("❌ Bronze layer not found. Run 01_bronze_layer_pandas.py first!")
    exit(1)

df = pd.read_parquet(bronze_file)
initial_count = len(df)
print(f"✅ Loaded {initial_count:,} records from Bronze layer\n")

# ==============================================================================
# DATA CLEANING
# ==============================================================================

print("=" * 80)
print("DATA CLEANING")
print("=" * 80)

# 1. Remove exact duplicates
print("\n1️⃣ Removing duplicates...")
duplicates_before = df.duplicated().sum()
df = df.drop_duplicates()
duplicates_removed = duplicates_before - df.duplicated().sum()
print(f"   Removed {duplicates_removed:,} duplicate records")
print(f"   Remaining: {len(df):,} records")

# 2. Handle null values in critical fields
print("\n2️⃣ Handling null values...")
nulls_before = df['reading_value'].isnull().sum()

# Flag records with null readings
df['quality_flag'] = 'VALID'
df.loc[df['reading_value'].isnull(), 'quality_flag'] = 'NULL_READING'

# For sensor readings, we'll keep the nulls but flag them
print(f"   Found {nulls_before:,} null readings")
print(f"   Flagged null readings for review")

# 3. Validate sensor value ranges
print("\n3️⃣ Validating sensor ranges...")

# Define valid ranges for each sensor type
valid_ranges = {
    'temperature': (0, 50),      # Celsius
    'humidity': (0, 100),         # Percent
    'pressure': (900, 1100),      # hPa
    'light': (0, 1500),           # lux
}

outliers_found = 0
for sensor_type, (min_val, max_val) in valid_ranges.items():
    mask = (df['sensor_type'] == sensor_type) & \
           (df['reading_value'].notna()) & \
           ((df['reading_value'] < min_val) | (df['reading_value'] > max_val))
    
    outlier_count = mask.sum()
    if outlier_count > 0:
        df.loc[mask, 'quality_flag'] = 'OUT_OF_RANGE'
        print(f"   {sensor_type:15} : {outlier_count:4} out-of-range values")
        outliers_found += outlier_count

print(f"   Total outliers flagged: {outliers_found:,}")

# 4. Validate battery levels
print("\n4️⃣ Checking battery levels...")
low_battery = (df['battery_level'] < 20).sum()
if low_battery > 0:
    print(f"   ⚠️  {low_battery:,} devices with low battery (<20%)")
    df.loc[df['battery_level'] < 20, 'alert_low_battery'] = True
    df['alert_low_battery'] = df['alert_low_battery'].fillna(False)
else:
    df['alert_low_battery'] = False

# 5. Standardize timestamps
print("\n5️⃣ Standardizing timestamps...")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['reading_hour'] = df['timestamp'].dt.hour
df['reading_day_of_week'] = df['timestamp'].dt.dayofweek
print(f"   ✅ Timestamps parsed and standardized")

# 6. Create derived features
print("\n6️⃣ Creating derived features...")
df['reading_date'] = df['timestamp'].dt.date
df['processing_timestamp'] = datetime.now()
print(f"   ✅ Added derived time features")

# ==============================================================================
# DATA QUALITY REPORT
# ==============================================================================

print("\n" + "=" * 80)
print("DATA QUALITY REPORT")
print("=" * 80)

quality_summary = df['quality_flag'].value_counts()
print("\n📊 Quality Flag Distribution:")
for flag, count in quality_summary.items():
    pct = (count / len(df)) * 100
    print(f"   {flag:20} : {count:6,} ({pct:5.2f}%)")

# Battery health
print(f"\n🔋 Battery Health:")
print(f"   Low battery alerts: {df['alert_low_battery'].sum():,}")
print(f"   Average battery level: {df['battery_level'].mean():.1f}%")

# Sensor distribution
print(f"\n📡 Sensor Distribution:")
sensor_dist = df['sensor_type'].value_counts()
for sensor, count in sensor_dist.items():
    pct = (count / len(df)) * 100
    print(f"   {sensor:15} : {count:6,} ({pct:5.2f}%)")

# Location distribution
print(f"\n📍 Location Distribution:")
location_dist = df['location'].value_counts()
for location, count in location_dist.items():
    pct = (count / len(df)) * 100
    print(f"   {location:15} : {count:6,} ({pct:5.2f}%)")

# ==============================================================================
# WRITE TO SILVER LAYER
# ==============================================================================

print("\n" + "=" * 80)
print("WRITING TO SILVER LAYER")
print("=" * 80)

output_file = SILVER_DIR / "sensors_silver.parquet"
df.to_parquet(
    output_file,
    engine='pyarrow',
    compression='snappy',
    index=False,
    partition_cols=['reading_date']
)

print(f"✅ Data written to: {output_file}")

# Verify
df_verify = pd.read_parquet(output_file)
print(f"✅ Verified: {len(df_verify):,} records")

# ==============================================================================
# SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("SILVER LAYER SUMMARY")
print("=" * 80)
print(f"📊 Input Records (Bronze):  {initial_count:,}")
print(f"📊 Output Records (Silver): {len(df):,}")
print(f"📊 Records Removed:         {initial_count - len(df):,}")
print(f"📊 Data Quality:")
print(f"   - Valid records:         {(df['quality_flag'] == 'VALID').sum():,}")
print(f"   - Flagged for review:    {(df['quality_flag'] != 'VALID').sum():,}")
print(f"   - Low battery alerts:    {df['alert_low_battery'].sum():,}")
print(f"✅ Output: {SILVER_DIR}")
print("=" * 80)

print("\n✅ SILVER LAYER PROCESSING COMPLETE!")
print("\nNext step: Run 03_gold_layer_pandas.py for business analytics")
