"""
Sample IoT Sensor Data Generator

Generates realistic IoT sensor data for testing the Medallion Architecture pipeline.
Creates data in JSON format simulating temperature, pressure, humidity, and vibration sensors.
"""

import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IoTDataGenerator:
    """Generate realistic IoT sensor data"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize data generator
        
        Args:
            seed: Random seed for reproducibility
        """
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
        
        # Sensor types and their value ranges
        self.sensor_configs = {
            "temperature": {
                "unit": "celsius",
                "normal_range": (18, 30),
                "critical_range": (-50, 150),
                "sensor_ids": [f"TEMP_{i:03d}" for i in range(1, 21)]
            },
            "pressure": {
                "unit": "psi",
                "normal_range": (14, 16),
                "critical_range": (0, 1000),
                "sensor_ids": [f"PRES_{i:03d}" for i in range(1, 11)]
            },
            "humidity": {
                "unit": "percent",
                "normal_range": (30, 70),
                "critical_range": (0, 100),
                "sensor_ids": [f"HUMI_{i:03d}" for i in range(1, 11)]
            },
            "vibration": {
                "unit": "mm/s",
                "normal_range": (0, 10),
                "critical_range": (0, 500),
                "sensor_ids": [f"VIBR_{i:03d}" for i in range(1, 11)]
            }
        }
        
        self.locations = [
            "Factory_A_Floor1", "Factory_A_Floor2", "Factory_A_Floor3",
            "Factory_B_Floor1", "Factory_B_Floor2",
            "Factory_C_Assembly", "Factory_C_Testing",
            "Warehouse_1_Zone_A", "Warehouse_1_Zone_B",
            "Warehouse_2_Storage"
        ]
    
    def generate_reading(
        self,
        sensor_type: str,
        sensor_id: str,
        timestamp: datetime,
        is_anomaly: bool = False
    ) -> Dict:
        """
        Generate a single sensor reading
        
        Args:
            sensor_type: Type of sensor (temperature, pressure, etc.)
            sensor_id: Unique sensor identifier
            timestamp: Reading timestamp
            is_anomaly: Whether to generate an anomalous value
            
        Returns:
            Dictionary with sensor reading data
        """
        config = self.sensor_configs[sensor_type]
        
        if is_anomaly:
            # Generate anomalous value outside normal range
            critical_low, critical_high = config["critical_range"]
            normal_low, normal_high = config["normal_range"]
            
            if random.choice([True, False]):
                # Too high
                value = random.uniform(normal_high + 5, critical_high)
            else:
                # Too low
                value = random.uniform(critical_low, normal_low - 5)
            
            status = "CRITICAL"
        else:
            # Generate normal value
            low, high = config["normal_range"]
            value = random.uniform(low, high)
            status = "NORMAL"
        
        # Add some occasional nulls and data quality issues
        if random.random() < 0.02:  # 2% chance
            value = None
        
        reading = {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "timestamp": timestamp.isoformat(),
            "reading_value": round(value, 2) if value is not None else None,
            "unit": config["unit"],
            "status": status,
            "location": random.choice(self.locations),
            "battery_level": round(random.uniform(20, 100), 1),
            "signal_strength": random.randint(1, 5),
        }
        
        # Occasionally add malformed data (for testing data quality)
        if random.random() < 0.01:  # 1% chance
            reading["corrupted_field"] = "THIS_SHOULD_NOT_BE_HERE"
        
        return reading
    
    def generate_batch(
        self,
        start_date: datetime,
        end_date: datetime,
        records_per_day: int = 100,
        anomaly_rate: float = 0.02
    ) -> List[Dict]:
        """
        Generate a batch of sensor readings
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            records_per_day: Number of readings per day per sensor
            anomaly_rate: Percentage of anomalous readings (0.0 to 1.0)
            
        Returns:
            List of sensor reading dictionaries
        """
        readings = []
        current_date = start_date
        
        logger.info(f"Generating data from {start_date} to {end_date}")
        logger.info(f"Records per day: {records_per_day}, Anomaly rate: {anomaly_rate * 100}%")
        
        while current_date <= end_date:
            for sensor_type, config in self.sensor_configs.items():
                for sensor_id in config["sensor_ids"]:
                    for _ in range(records_per_day):
                        # Generate random time within the day
                        random_time = current_date + timedelta(
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59),
                            seconds=random.randint(0, 59)
                        )
                        
                        # Determine if this reading should be anomalous
                        is_anomaly = random.random() < anomaly_rate
                        
                        reading = self.generate_reading(
                            sensor_type, sensor_id, random_time, is_anomaly
                        )
                        readings.append(reading)
            
            current_date += timedelta(days=1)
        
        logger.info(f"Generated {len(readings):,} total readings")
        return readings
    
    def save_to_json(self, readings: List[Dict], output_path: str, split_files: int = 1) -> None:
        """
        Save readings to JSON file(s)
        
        Args:
            readings: List of reading dictionaries
            output_path: Output directory path
            split_files: Number of files to split data into (for testing multiple files)
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if split_files == 1:
            # Single file
            output_file = output_dir / "sensor_data.json"
            with open(output_file, 'w') as f:
                json.dump(readings, f, indent=2)
            logger.info(f"Saved {len(readings):,} readings to {output_file}")
        else:
            # Multiple files
            chunk_size = len(readings) // split_files
            for i in range(split_files):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < split_files - 1 else len(readings)
                chunk = readings[start_idx:end_idx]
                
                output_file = output_dir / f"sensor_data_part_{i+1:03d}.json"
                with open(output_file, 'w') as f:
                    json.dump(chunk, f, indent=2)
                logger.info(f"Saved {len(chunk):,} readings to {output_file}")
    
    def save_to_csv(self, readings: List[Dict], output_path: str) -> None:
        """
        Save readings to CSV file
        
        Args:
            readings: List of reading dictionaries
            output_path: Output file path
        """
        import csv
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if readings:
            fieldnames = readings[0].keys()
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(readings)
            logger.info(f"Saved {len(readings):,} readings to {output_file}")
    
    def generate_streaming_data(
        self,
        duration_seconds: int = 60,
        rate_per_second: int = 10
    ) -> List[Dict]:
        """
        Generate streaming-like data with recent timestamps
        
        Args:
            duration_seconds: Duration of data generation in seconds
            rate_per_second: Number of readings per second
            
        Returns:
            List of recent sensor readings
        """
        readings = []
        start_time = datetime.now() - timedelta(seconds=duration_seconds)
        
        for i in range(duration_seconds):
            timestamp = start_time + timedelta(seconds=i)
            
            for _ in range(rate_per_second):
                sensor_type = random.choice(list(self.sensor_configs.keys()))
                config = self.sensor_configs[sensor_type]
                sensor_id = random.choice(config["sensor_ids"])
                
                reading = self.generate_reading(sensor_type, sensor_id, timestamp)
                readings.append(reading)
        
        logger.info(f"Generated {len(readings):,} streaming readings")
        return readings


def main():
    """Main function to generate sample data"""
    
    logger.info("=" * 70)
    logger.info("IoT Sensor Data Generator")
    logger.info("=" * 70)
    
    # Initialize generator
    generator = IoTDataGenerator(seed=42)
    
    # Project paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "sample"
    
    # Generate historical batch data (30 days)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 30)
    
    historical_data = generator.generate_batch(
        start_date=start_date,
        end_date=end_date,
        records_per_day=50,  # 50 readings per day per sensor
        anomaly_rate=0.02  # 2% anomalies
    )
    
    # Save historical data to multiple JSON files (simulating multiple data sources)
    generator.save_to_json(
        historical_data,
        str(data_dir / "historical"),
        split_files=5
    )
    
    # Generate recent streaming-like data
    streaming_data = generator.generate_streaming_data(
        duration_seconds=3600,  # 1 hour
        rate_per_second=5
    )
    
    generator.save_to_json(
        streaming_data,
        str(data_dir / "streaming"),
        split_files=1
    )
    
    # Generate a small sample for quick testing
    test_data = generator.generate_batch(
        start_date=datetime(2024, 2, 18),
        end_date=datetime(2024, 2, 18),
        records_per_day=10,
        anomaly_rate=0.05
    )
    
    generator.save_to_json(
        test_data,
        str(data_dir / "test"),
        split_files=1
    )
    
    # Also save as CSV for easy viewing
    generator.save_to_csv(
        test_data[:1000],  # First 1000 records
        str(data_dir / "test" / "sensor_data_sample.csv")
    )
    
    logger.info("=" * 70)
    logger.info("Data generation complete!")
    logger.info(f"Output directory: {data_dir}")
    logger.info("=" * 70)
    
    # Print summary
    print("\n📊 Data Summary:")
    print(f"  Historical data: {len(historical_data):,} records (30 days)")
    print(f"  Streaming data: {len(streaming_data):,} records (1 hour)")
    print(f"  Test data: {len(test_data):,} records (1 day)")
    print(f"\n📁 Files created in: {data_dir}")
    print("  ├── historical/ (5 JSON files)")
    print("  ├── streaming/ (1 JSON file)")
    print("  └── test/ (1 JSON file + 1 CSV sample)")


if __name__ == "__main__":
    main()
