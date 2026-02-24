"""
SIMPLE DATA GENERATOR (No Spark Required)

Generates sample IoT sensor data in JSON format without using Spark.
This is a Windows-compatible alternative for local development.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# Configuration
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data" / "sample"
NUM_RECORDS = 10000
BATCH_SIZE = 1000

# Create data directory
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("GENERATING SAMPLE IOT SENSOR DATA (No Spark)")
print("=" * 80)
print(f"\n📁 Output Directory: {DATA_DIR}")
print(f"📊 Total Records: {NUM_RECORDS:,}")
print(f"📦 Batch Size: {BATCH_SIZE:,}\n")

# Sensor types and their characteristics
SENSOR_TYPES = {
    "temperature": {"min": 15.0, "max": 35.0, "unit": "celsius"},
    "humidity": {"min": 30.0, "max": 80.0, "unit": "percent"},
    "pressure": {"min": 980.0, "max": 1020.0, "unit": "hPa"},
    "light": {"min": 0.0, "max": 1000.0, "unit": "lux"},
}

LOCATIONS = ["Building_A", "Building_B", "Building_C", "Warehouse_1", "Warehouse_2"]
DEVICE_IDS = [f"SENSOR_{i:04d}" for i in range(1, 51)]

# Generate data in batches
start_time = datetime.now() - timedelta(days=7)
records_generated = 0
batch_num = 1

while records_generated < NUM_RECORDS:
    batch_records = []
    batch_end = min(records_generated + BATCH_SIZE, NUM_RECORDS)
    
    for i in range(records_generated, batch_end):
        # Random timestamp within the last 7 days
        timestamp = start_time + timedelta(
            minutes=random.randint(0, 7 * 24 * 60)
        )
        
        # Random sensor type
        sensor_type = random.choice(list(SENSOR_TYPES.keys()))
        sensor_config = SENSOR_TYPES[sensor_type]
        
        # Generate reading with occasional anomalies
        if random.random() < 0.05:  # 5% anomalies
            reading_value = random.uniform(
                sensor_config["min"] * 0.5,
                sensor_config["max"] * 1.5
            )
        else:
            reading_value = random.uniform(
                sensor_config["min"],
                sensor_config["max"]
            )
        
        # Occasional null values (data quality issues)
        if random.random() < 0.02:  # 2% null values
            reading_value = None
        
        # Create record
        record = {
            "device_id": random.choice(DEVICE_IDS),
            "sensor_type": sensor_type,
            "reading_value": round(reading_value, 2) if reading_value else None,
            "unit": sensor_config["unit"],
            "location": random.choice(LOCATIONS),
            "timestamp": timestamp.isoformat(),
            "battery_level": round(random.uniform(20, 100), 1),
            "signal_strength": random.randint(-90, -30),
            "firmware_version": f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        }
        
        batch_records.append(record)
    
    # Write batch to file
    output_file = DATA_DIR / f"sensors_batch_{batch_num:03d}.json"
    with open(output_file, 'w') as f:
        for record in batch_records:
            f.write(json.dumps(record) + '\n')
    
    records_generated = batch_end
    print(f"✅ Batch {batch_num}: Generated {len(batch_records):,} records -> {output_file.name}")
    batch_num += 1

print(f"\n{'=' * 80}")
print(f"✅ SUCCESS: Generated {NUM_RECORDS:,} sensor records in {batch_num - 1} batches")
print(f"📁 Location: {DATA_DIR}")
print(f"{'=' * 80}\n")

# Display sample records
print("Sample Records (first 3):")
print("-" * 80)
with open(DATA_DIR / "sensors_batch_001.json", 'r') as f:
    for i, line in enumerate(f):
        if i >= 3:
            break
        record = json.loads(line)
        print(json.dumps(record, indent=2))
        print()

print("\n✅ SAMPLE DATA GENERATION COMPLETE!")
print("\nNext steps:")
print("  1. Check the data/sample/ directory for JSON files")
print("  2. Run the Bronze layer ingestion notebook (if Spark is working)")
print("  3. Or use pandas to process the data locally")
