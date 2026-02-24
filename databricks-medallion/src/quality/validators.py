"""
Data Quality Validators

Comprehensive data quality checks for the Medallion Architecture pipeline.
Includes null checks, duplicate detection, schema validation, and business rule validation.
"""

import logging
from typing import Dict, List, Tuple, Optional
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityValidator:
    """Comprehensive data quality validation framework"""
    
    def __init__(self, spark: SparkSession):
        """
        Initialize validator
        
        Args:
            spark: SparkSession object
        """
        self.spark = spark
        self.validation_results = []
    
    def check_null_rate(
        self,
        df: DataFrame,
        column: str,
        threshold: float = 0.05
    ) -> Tuple[bool, Dict]:
        """
        Check if null rate in column is below threshold
        
        Args:
            df: DataFrame to check
            column: Column name to check
            threshold: Maximum allowed null rate (0.05 = 5%)
        
        Returns:
            Tuple of (passed: bool, metrics: dict)
        """
        total_count = df.count()
        if total_count == 0:
            return True, {"null_count": 0, "null_rate": 0.0, "threshold": threshold}
        
        null_count = df.filter(F.col(column).isNull()).count()
        null_rate = null_count / total_count
        passed = null_rate <= threshold
        
        result = {
            "check_name": f"null_rate_{column}",
            "column": column,
            "total_count": total_count,
            "null_count": null_count,
            "null_rate": round(null_rate, 4),
            "threshold": threshold,
            "passed": passed
        }
        
        if not passed:
            logger.warning(f"❌ Null rate check FAILED for {column}: {null_rate:.2%} > {threshold:.2%}")
        else:
            logger.info(f"✅ Null rate check PASSED for {column}: {null_rate:.2%} <= {threshold:.2%}")
        
        self.validation_results.append(result)
        return passed, result
    
    def check_duplicates(
        self,
        df: DataFrame,
        key_columns: List[str],
        threshold: float = 0.01
    ) -> Tuple[bool, Dict]:
        """
        Check for duplicate records
        
        Args:
            df: DataFrame to check
            key_columns: Columns that define uniqueness
            threshold: Maximum allowed duplicate rate
            
        Returns:
            Tuple of (passed: bool, metrics: dict)
        """
        total_count = df.count()
        unique_count = df.dropDuplicates(key_columns).count()
        duplicate_count = total_count - unique_count
        duplicate_rate = duplicate_count / total_count if total_count > 0 else 0
        passed = duplicate_rate <= threshold
        
        result = {
            "check_name": "duplicate_check",
            "key_columns": key_columns,
            "total_count": total_count,
            "unique_count": unique_count,
            "duplicate_count": duplicate_count,
            "duplicate_rate": round(duplicate_rate, 4),
            "threshold": threshold,
            "passed": passed
        }
        
        if not passed:
            logger.warning(f"❌ Duplicate check FAILED: {duplicate_count} duplicates ({duplicate_rate:.2%})")
        else:
            logger.info(f"✅ Duplicate check PASSED: {duplicate_count} duplicates ({duplicate_rate:.2%})")
        
        self.validation_results.append(result)
        return passed, result
    
    def check_value_range(
        self,
        df: DataFrame,
        column: str,
        min_value: float,
        max_value: float
    ) -> Tuple[bool, Dict]:
        """
        Check if values are within expected range
        
        Args:
            df: DataFrame to check
            column: Column name to check
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Tuple of (passed: bool, metrics: dict)
        """
        total_count = df.filter(F.col(column).isNotNull()).count()
        out_of_range_count = df.filter(
            (F.col(column) < min_value) | (F.col(column) > max_value)
        ).count()
        
        out_of_range_rate = out_of_range_count / total_count if total_count > 0 else 0
        passed = out_of_range_count == 0
        
        result = {
            "check_name": f"value_range_{column}",
            "column": column,
            "min_value": min_value,
            "max_value": max_value,
            "total_count": total_count,
            "out_of_range_count": out_of_range_count,
            "out_of_range_rate": round(out_of_range_rate, 4),
            "passed": passed
        }
        
        if not passed:
            logger.warning(f"❌ Range check FAILED for {column}: {out_of_range_count} values out of range")
        else:
            logger.info(f"✅ Range check PASSED for {column}: All values in range [{min_value}, {max_value}]")
        
        self.validation_results.append(result)
        return passed, result
    
    def check_schema(
        self,
        df: DataFrame,
        expected_schema: StructType
    ) -> Tuple[bool, Dict]:
        """
        Validate DataFrame schema
        
        Args:
            df: DataFrame to check
            expected_schema: Expected schema
            
        Returns:
            Tuple of (passed: bool, metrics: dict)
        """
        actual_schema = df.schema
        passed = actual_schema == expected_schema
        
        # Find differences
        expected_fields = {f.name: f.dataType for f in expected_schema.fields}
        actual_fields = {f.name: f.dataType for f in actual_schema.fields}
        
        missing_columns = set(expected_fields.keys()) - set(actual_fields.keys())
        extra_columns = set(actual_fields.keys()) - set(expected_fields.keys())
        type_mismatches = {
            col: (expected_fields[col], actual_fields[col])
            for col in expected_fields.keys() & actual_fields.keys()
            if expected_fields[col] != actual_fields[col]
        }
        
        result = {
            "check_name": "schema_validation",
            "passed": passed,
            "missing_columns": list(missing_columns),
            "extra_columns": list(extra_columns),
            "type_mismatches": {k: (str(v[0]), str(v[1])) for k, v in type_mismatches.items()}
        }
        
        if not passed:
            logger.warning(f"❌ Schema validation FAILED")
            if missing_columns:
                logger.warning(f"  Missing columns: {missing_columns}")
            if extra_columns:
                logger.warning(f"  Extra columns: {extra_columns}")
            if type_mismatches:
                logger.warning(f"  Type mismatches: {type_mismatches}")
        else:
            logger.info(f"✅ Schema validation PASSED")
        
        self.validation_results.append(result)
        return passed, result
    
    def check_data_freshness(
        self,
        df: DataFrame,
        timestamp_column: str,
        max_age_hours: int = 24
    ) -> Tuple[bool, Dict]:
        """
        Check if data is fresh (not too old)
        
        Args:
            df: DataFrame to check
            timestamp_column: Column with timestamp
            max_age_hours: Maximum allowed age in hours
            
        Returns:
            Tuple of (passed: bool, metrics: dict)
        """
        current_time = datetime.now()
        
        # Get latest timestamp
        latest_timestamp_row = df.agg(F.max(timestamp_column).alias("latest")).collect()
        if not latest_timestamp_row or latest_timestamp_row[0]["latest"] is None:
            return False, {
                "check_name": "data_freshness",
                "passed": False,
                "error": "No valid timestamps found"
            }
        
        latest_timestamp = latest_timestamp_row[0]["latest"]
        
        # Calculate age
        if isinstance(latest_timestamp, str):
            latest_timestamp = datetime.fromisoformat(latest_timestamp)
        
        age_hours = (current_time - latest_timestamp).total_seconds() / 3600
        passed = age_hours <= max_age_hours
        
        result = {
            "check_name": "data_freshness",
            "timestamp_column": timestamp_column,
            "latest_timestamp": str(latest_timestamp),
            "age_hours": round(age_hours, 2),
            "max_age_hours": max_age_hours,
            "passed": passed
        }
        
        if not passed:
            logger.warning(f"❌ Freshness check FAILED: Data is {age_hours:.1f} hours old (max: {max_age_hours}h)")
        else:
            logger.info(f"✅ Freshness check PASSED: Data is {age_hours:.1f} hours old")
        
        self.validation_results.append(result)
        return passed, result
    
    def check_referential_integrity(
        self,
        fact_df: DataFrame,
        dimension_df: DataFrame,
        join_key: str
    ) -> Tuple[bool, Dict]:
        """
        Check referential integrity between fact and dimension tables
        
        Args:
            fact_df: Fact table DataFrame
            dimension_df: Dimension table DataFrame
            join_key: Column to join on
            
        Returns:
            Tuple of (passed: bool, metrics: dict)
        """
        # Find orphan records (records in fact not in dimension)
        orphan_count = fact_df.join(
            dimension_df,
            on=join_key,
            how="left_anti"
        ).count()
        
        total_count = fact_df.count()
        passed = orphan_count == 0
        
        result = {
            "check_name": "referential_integrity",
            "join_key": join_key,
            "total_records": total_count,
            "orphan_records": orphan_count,
            "passed": passed
        }
        
        if not passed:
            logger.warning(f"❌ Referential integrity FAILED: {orphan_count} orphan records")
        else:
            logger.info(f"✅ Referential integrity PASSED: No orphan records")
        
        self.validation_results.append(result)
        return passed, result
    
    def run_all_checks(
        self,
        df: DataFrame,
        checks_config: Dict
    ) -> Tuple[bool, List[Dict]]:
        """
        Run all configured quality checks
        
        Args:
            df: DataFrame to validate
            checks_config: Configuration dictionary with check parameters
            
        Returns:
            Tuple of (all_passed: bool, results: list)
        """
        logger.info("=" * 70)
        logger.info("Running Data Quality Checks")
        logger.info("=" * 70)
        
        all_passed = True
        
        # Null rate checks
        if "null_checks" in checks_config:
            for column, threshold in checks_config["null_checks"].items():
                if column in df.columns:
                    passed, _ = self.check_null_rate(df, column, threshold)
                    all_passed = all_passed and passed
        
        # Duplicate check
        if "duplicate_check" in checks_config:
            key_columns = checks_config["duplicate_check"]["keys"]
            threshold = checks_config["duplicate_check"].get("threshold", 0.01)
            passed, _ = self.check_duplicates(df, key_columns, threshold)
            all_passed = all_passed and passed
        
        # Range checks
        if "range_checks" in checks_config:
            for column, ranges in checks_config["range_checks"].items():
                if column in df.columns:
                    passed, _ = self.check_value_range(
                        df, column, ranges["min"], ranges["max"]
                    )
                    all_passed = all_passed and passed
        
        # Freshness check
        if "freshness_check" in checks_config:
            timestamp_col = checks_config["freshness_check"]["column"]
            max_age = checks_config["freshness_check"]["max_age_hours"]
            passed, _ = self.check_data_freshness(df, timestamp_col, max_age)
            all_passed = all_passed and passed
        
        logger.info("=" * 70)
        if all_passed:
            logger.info("✅ All quality checks PASSED")
        else:
            logger.warning("❌ Some quality checks FAILED")
        logger.info(f"Total checks run: {len(self.validation_results)}")
        logger.info("=" * 70)
        
        return all_passed, self.validation_results
    
    def get_validation_summary(self) -> DataFrame:
        """
        Get validation results as DataFrame
        
        Returns:
            DataFrame with validation results
        """
        if not self.validation_results:
            return self.spark.createDataFrame([], "check_name STRING, passed BOOLEAN")
        
        return self.spark.createDataFrame(self.validation_results)
    
    def clear_results(self):
        """Clear validation results"""
        self.validation_results = []


# Example usage
if __name__ == "__main__":
    from pyspark.sql import SparkSession
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("DataQualityValidatorTest") \
        .getOrCreate()
    
    # Create sample data
    data = [
        ("sensor_1", "2024-02-18 10:00:00", 25.5, "temperature"),
        ("sensor_2", "2024-02-18 10:01:00", 26.0, "temperature"),
        ("sensor_3", "2024-02-18 10:02:00", None, "temperature"),  # Null value
        ("sensor_1", "2024-02-18 10:00:00", 25.5, "temperature"),  # Duplicate
    ]
    df = spark.createDataFrame(
        data,
        ["sensor_id", "timestamp", "reading_value", "sensor_type"]
    )
    
    # Initialize validator
    validator = DataQualityValidator(spark)
    
    # Run individual checks
    validator.check_null_rate(df, "reading_value", threshold=0.2)
    validator.check_duplicates(df, ["sensor_id", "timestamp"], threshold=0.3)
    validator.check_value_range(df, "reading_value", min_value=0, max_value=100)
    
    # Get summary
    summary_df = validator.get_validation_summary()
    summary_df.show(truncate=False)
    
    spark.stop()
