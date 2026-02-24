"""
GOLD LAYER - PANDAS VERSION (Windows Compatible)

Create business-level aggregations and analytics from Silver layer.

Purpose:
    - Daily sensor averages
    - Location-based analytics
    - Device health metrics
    - Anomaly detection summaries
    - Business KPIs
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("GOLD LAYER - BUSINESS ANALYTICS (Pandas Version)")
print("=" * 80)

# Configuration
PROJECT_ROOT = Path(__file__).parent
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"

# Create gold directory
GOLD_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n📁 Source: {SILVER_DIR}")
print(f"📁 Target: {GOLD_DIR}\n")

# Read Silver data
print("Reading Silver layer data...")
silver_file = SILVER_DIR / "sensors_silver.parquet"

if not silver_file.exists():
    print("❌ Silver layer not found. Run 02_silver_layer_pandas.py first!")
    exit(1)

df = pd.read_parquet(silver_file)
initial_count = len(df)
print(f"✅ Loaded {initial_count:,} records from Silver layer\n")

# Filter to VALID records only for analytics
df_valid = df[df['quality_flag'] == 'VALID'].copy()
print(f"📊 Using {len(df_valid):,} valid records for analytics\n")

# ==============================================================================
# AGGREGATION 1: DAILY SENSOR AVERAGES BY LOCATION
# ==============================================================================

print("=" * 80)
print("AGGREGATION 1: Daily Sensor Averages by Location")
print("=" * 80)

daily_avg = df_valid.groupby(['reading_date', 'location', 'sensor_type']).agg({
    'reading_value': ['mean', 'min', 'max', 'std', 'count'],
    'device_id': 'nunique'
}).reset_index()

# Flatten column names
daily_avg.columns = [
    'date', 'location', 'sensor_type',
    'avg_reading', 'min_reading', 'max_reading', 'std_reading', 'reading_count',
    'device_count'
]

daily_avg['created_at'] = datetime.now()
print(f"✅ Created {len(daily_avg):,} daily aggregation records")
print(f"\nSample data:")
print(daily_avg.head(10))

# Write to parquet
output_file_1 = GOLD_DIR / "daily_sensor_averages.parquet"
daily_avg.to_parquet(output_file_1, engine='pyarrow', compression='snappy', index=False)
print(f"\n✅ Saved to: {output_file_1.name}")

# ==============================================================================
# AGGREGATION 2: DEVICE HEALTH METRICS
# ==============================================================================

print("\n" + "=" * 80)
print("AGGREGATION 2: Device Health Metrics")
print("=" * 80)

device_health = df.groupby('device_id').agg({
    'battery_level': 'mean',
    'signal_strength': 'mean',
    'timestamp': ['min', 'max', 'count'],
    'quality_flag': lambda x: (x != 'VALID').sum(),  # Count of invalid readings
    'reading_value': lambda x: x.isnull().sum(),  # Count of null readings
}).reset_index()

# Flatten column names
device_health.columns = [
    'device_id',
    'avg_battery_level',
    'avg_signal_strength',
    'first_reading_time',
    'last_reading_time',
    'total_readings',
    'invalid_reading_count',
    'null_reading_count'
]

# Calculate health score (0-100)
device_health['health_score'] = (
    (device_health['avg_battery_level'] * 0.4) +
    ((device_health['avg_signal_strength'] + 90) / 60 * 100 * 0.3) +
    ((1 - device_health['invalid_reading_count'] / device_health['total_readings']) * 100 * 0.3)
).round(1)

device_health['status'] = pd.cut(
    device_health['health_score'],
    bins=[0, 50, 75, 100],
    labels=['CRITICAL', 'WARNING', 'HEALTHY']
)

device_health['created_at'] = datetime.now()
print(f"✅ Created health metrics for {len(device_health):,} devices")
print(f"\nDevice Status Distribution:")
print(device_health['status'].value_counts())
print(f"\nSample data:")
print(device_health.head(10))

# Write to parquet
output_file_2 = GOLD_DIR / "device_health_metrics.parquet"
device_health.to_parquet(output_file_2, engine='pyarrow', compression='snappy', index=False)
print(f"\n✅ Saved to: {output_file_2.name}")

# ==============================================================================
# AGGREGATION 3: LOCATION PERFORMANCE SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("AGGREGATION 3: Location Performance Summary")
print("=" * 80)

location_summary = df_valid.groupby('location').agg({
    'device_id': 'nunique',
    'reading_value': ['count', 'mean', 'std'],
    'battery_level': 'mean',
    'timestamp': ['min', 'max']
}).reset_index()

# Flatten column names
location_summary.columns = [
    'location',
    'total_devices',
    'total_readings',
    'avg_reading_value',
    'std_reading_value',
    'avg_battery_level',
    'first_reading',
    'last_reading'
]

# Calculate reading frequency (readings per device)
location_summary['readings_per_device'] = (
    location_summary['total_readings'] / location_summary['total_devices']
).round(0).astype(int)

# Add quality metrics
quality_by_location = df.groupby('location').agg({
    'quality_flag': lambda x: (x == 'VALID').sum() / len(x) * 100
}).reset_index()
quality_by_location.columns = ['location', 'data_quality_pct']

location_summary = location_summary.merge(quality_by_location, on='location')
location_summary['created_at'] = datetime.now()

print(f"✅ Created summary for {len(location_summary):,} locations")
print(f"\n{location_summary}")

# Write to parquet
output_file_3 = GOLD_DIR / "location_performance.parquet"
location_summary.to_parquet(output_file_3, engine='pyarrow', compression='snappy', index=False)
print(f"\n✅ Saved to: {output_file_3.name}")

# ==============================================================================
# AGGREGATION 4: HOURLY TRENDS
# ==============================================================================

print("\n" + "=" * 80)
print("AGGREGATION 4: Hourly Sensor Trends")
print("=" * 80)

hourly_trends = df_valid.groupby(['reading_hour', 'sensor_type']).agg({
    'reading_value': ['mean', 'std', 'count'],
}).reset_index()

# Flatten column names
hourly_trends.columns = [
    'hour_of_day', 'sensor_type',
    'avg_reading', 'std_reading', 'reading_count'
]

hourly_trends['created_at'] = datetime.now()
print(f"✅ Created hourly trends for {len(hourly_trends):,} hour-sensor combinations")
print(f"\nSample hourly trends (Temperature):")
print(hourly_trends[hourly_trends['sensor_type'] == 'temperature'].head(24))

# Write to parquet
output_file_4 = GOLD_DIR / "hourly_sensor_trends.parquet"
hourly_trends.to_parquet(output_file_4, engine='pyarrow', compression='snappy', index=False)
print(f"\n✅ Saved to: {output_file_4.name}")

# ==============================================================================
# AGGREGATION 5: DATA QUALITY METRICS
# ==============================================================================

print("\n" + "=" * 80)
print("AGGREGATION 5: Data Quality Metrics")
print("=" * 80)

quality_metrics = df.groupby('reading_date').agg({
    'quality_flag': [
        ('total_records', 'count'),
        ('valid_records', lambda x: (x == 'VALID').sum()),
        ('null_records', lambda x: (x == 'NULL_READING').sum()),
        ('out_of_range_records', lambda x: (x == 'OUT_OF_RANGE').sum())
    ]
}).reset_index()

# Flatten column names
quality_metrics.columns = ['date', 'total_records', 'valid_records', 'null_records', 'out_of_range_records']

quality_metrics['quality_score'] = (
    quality_metrics['valid_records'] / quality_metrics['total_records'] * 100
).round(2)

quality_metrics['created_at'] = datetime.now()
print(f"✅ Created quality metrics for {len(quality_metrics):,} dates")
print(f"\n{quality_metrics}")

# Write to parquet
output_file_5 = GOLD_DIR / "data_quality_metrics.parquet"
quality_metrics.to_parquet(output_file_5, engine='pyarrow', compression='snappy', index=False)
print(f"\n✅ Saved to: {output_file_5.name}")

# ==============================================================================
# EXECUTIVE SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("EXECUTIVE SUMMARY - KEY METRICS")
print("=" * 80)

print(f"\n📊 Data Volume:")
print(f"   Total Records Processed: {initial_count:,}")
print(f"   Valid Records: {len(df_valid):,} ({len(df_valid)/initial_count*100:.1f}%)")
print(f"   Invalid Records: {initial_count - len(df_valid):,} ({(initial_count - len(df_valid))/initial_count*100:.1f}%)")

print(f"\n📡 Sensor Overview:")
print(f"   Total Devices: {df['device_id'].nunique()}")
print(f"   Total Locations: {df['location'].nunique()}")
print(f"   Sensor Types: {', '.join(df['sensor_type'].unique())}")

print(f"\n🏥 Device Health:")
healthy_devices = (device_health['status'] == 'HEALTHY').sum()
warning_devices = (device_health['status'] == 'WARNING').sum()
critical_devices = (device_health['status'] == 'CRITICAL').sum()
print(f"   Healthy: {healthy_devices} devices")
print(f"   Warning: {warning_devices} devices")
print(f"   Critical: {critical_devices} devices")

print(f"\n📈 Data Quality:")
overall_quality = (df['quality_flag'] == 'VALID').sum() / len(df) * 100
print(f"   Overall Quality Score: {overall_quality:.2f}%")

print(f"\n💾 Gold Layer Outputs:")
print(f"   1. {output_file_1.name} ({len(daily_avg):,} records)")
print(f"   2. {output_file_2.name} ({len(device_health):,} records)")
print(f"   3. {output_file_3.name} ({len(location_summary):,} records)")
print(f"   4. {output_file_4.name} ({len(hourly_trends):,} records)")
print(f"   5. {output_file_5.name} ({len(quality_metrics):,} records)")

print("\n" + "=" * 80)
print("✅ GOLD LAYER PROCESSING COMPLETE!")
print("=" * 80)
print("\n🎉 MEDALLION ARCHITECTURE PIPELINE COMPLETE!\n")
print("All layers processed successfully:")
print("  ✅ Bronze Layer (Raw Data)")
print("  ✅ Silver Layer (Cleaned & Validated)")
print("  ✅ Gold Layer (Business Analytics)\n")
print(f"📁 All data saved to: {GOLD_DIR.parent}")
