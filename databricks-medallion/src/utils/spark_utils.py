"""
Spark Utility Functions

Helper functions for common Spark operations used throughout the project.
"""

import logging
import os
import sys
from typing import Dict, List, Optional
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType
from delta import DeltaTable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spark_session(app_name: str, config: Dict[str, str] = None) -> SparkSession:
    """
    Create and configure Spark session with Delta Lake support
    
    Args:
        app_name: Name of the Spark application
        config: Optional dictionary of Spark configuration parameters
        
    Returns:
        Configured SparkSession object
    """
    # Handle Windows-specific Hadoop issues
    if sys.platform == "win32" and "HADOOP_HOME" not in os.environ:
        # Set up Hadoop home for Windows
        import tempfile
        import urllib.request
        
        hadoop_home = os.path.join(tempfile.gettempdir(), "hadoop")
        hadoop_bin = os.path.join(hadoop_home, "bin")
        os.makedirs(hadoop_bin, exist_ok=True)
        os.environ["HADOOP_HOME"] = hadoop_home
        
        # Download winutils.exe if not present
        winutils_path = os.path.join(hadoop_bin, "winutils.exe")
        if not os.path.exists(winutils_path):
            try:
                logger.info("Downloading winutils.exe for Windows...")
                # Download from a known repository
                url = "https://github.com/cdarlint/winutils/raw/master/hadoop-3.3.5/bin/winutils.exe"
                urllib.request.urlretrieve(url, winutils_path)
                logger.info(f"Downloaded winutils.exe to {winutils_path}")
            except Exception as e:
                logger.warning(f"Could not download winutils.exe: {e}")
                # Create a placeholder - Spark may still work in local mode
                with open(winutils_path, 'wb') as f:
                    pass
        
        logger.info(f"Set HADOOP_HOME to: {hadoop_home}")
    
    # Set Python executable explicitly for Spark workers
    python_exe = sys.executable
    os.environ["PYSPARK_PYTHON"] = python_exe
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_exe
    logger.info(f"Using Python executable: {python_exe}")
    
    builder = SparkSession.builder.appName(app_name)
    
    # Configure Delta Lake packages (for PySpark 3.5.x with Scala 2.12)
    builder = builder.config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.1")
    
    # Add default config for better Windows compatibility
    default_config = {
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        "spark.sql.warehouse.dir": "file:///tmp/spark-warehouse",
        "spark.driver.host": "localhost",
        "spark.driver.bindAddress": "127.0.0.1",
    }
    
    # Merge with user config
    if config:
        default_config.update(config)
    
    # Apply configuration
    for key, value in default_config.items():
        builder = builder.config(key, value)
    
    spark = builder.getOrCreate()
    
    # Set log level
    spark.sparkContext.setLogLevel("WARN")
    
    logger.info(f"Spark session created: {app_name}")
    logger.info(f"Spark version: {spark.version}")
    
    return spark


def read_delta_table(spark: SparkSession, path: str, version: Optional[int] = None) -> DataFrame:
    """
    Read Delta table with optional time travel
    
    Args:
        spark: SparkSession object
        path: Path to Delta table
        version: Optional version number for time travel
        
    Returns:
        DataFrame
    """
    reader = spark.read.format("delta")
    
    if version is not None:
        reader = reader.option("versionAsOf", version)
        logger.info(f"Reading Delta table from {path} at version {version}")
    else:
        logger.info(f"Reading Delta table from {path}")
    
    return reader.load(path)


def write_delta_table(
    df: DataFrame,
    path: str,
    mode: str = "append",
    partition_by: Optional[List[str]] = None,
    merge_schema: bool = False,
    overwrite_schema: bool = False
) -> None:
    """
    Write DataFrame to Delta table
    
    Args:
        df: DataFrame to write
        path: Destination path
        mode: Write mode (append, overwrite, etc.)
        partition_by: List of columns to partition by
        merge_schema: Whether to merge schema changes
        overwrite_schema: Whether to overwrite schema
    """
    writer = df.write.format("delta").mode(mode)
    
    if partition_by:
        writer = writer.partitionBy(*partition_by)
        logger.info(f"Partitioning by: {partition_by}")
    
    if merge_schema:
        writer = writer.option("mergeSchema", "true")
        logger.info("Schema merge enabled")
    
    if overwrite_schema:
        writer = writer.option("overwriteSchema", "true")
        logger.info("Schema overwrite enabled")
    
    logger.info(f"Writing to {path} in {mode} mode")
    writer.save(path)
    logger.info(f"Successfully wrote {df.count()} records")


def add_ingestion_metadata(df: DataFrame) -> DataFrame:
    """
    Add standard ingestion metadata columns to DataFrame
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with metadata columns added
    """
    return df.withColumn("ingestion_timestamp", F.current_timestamp()) \
             .withColumn("ingestion_date", F.current_date()) \
             .withColumn("source_file", F.input_file_name())


def deduplicate_dataframe(
    df: DataFrame,
    key_columns: List[str],
    order_by_column: str = "timestamp",
    ascending: bool = False
) -> DataFrame:
    """
    Remove duplicate records based on key columns
    
    Args:
        df: Input DataFrame
        key_columns: Columns to use for identifying duplicates
        order_by_column: Column to use for ordering when picking the record to keep
        ascending: Sort order (False = keep latest)
        
    Returns:
        Deduplicated DataFrame
    """
    from pyspark.sql.window import Window
    
    window_spec = Window.partitionBy(*key_columns).orderBy(
        F.col(order_by_column).asc() if ascending else F.col(order_by_column).desc()
    )
    
    deduped_df = df.withColumn("row_num", F.row_number().over(window_spec)) \
                   .filter(F.col("row_num") == 1) \
                   .drop("row_num")
    
    original_count = df.count()
    deduped_count = deduped_df.count()
    duplicates_removed = original_count - deduped_count
    
    logger.info(f"Deduplication complete: {duplicates_removed} duplicates removed")
    logger.info(f"Original: {original_count} | After: {deduped_count}")
    
    return deduped_df


def validate_schema(df: DataFrame, expected_schema: StructType) -> bool:
    """
    Validate DataFrame schema against expected schema
    
    Args:
        df: DataFrame to validate
        expected_schema: Expected StructType schema
        
    Returns:
        True if schema matches, False otherwise
    """
    actual_schema = df.schema
    
    if actual_schema == expected_schema:
        logger.info("Schema validation passed")
        return True
    else:
        logger.warning("Schema validation failed")
        logger.warning(f"Expected: {expected_schema}")
        logger.warning(f"Actual: {actual_schema}")
        return False


def optimize_delta_table(spark: SparkSession, path: str, zorder_columns: Optional[List[str]] = None) -> None:
    """
    Optimize Delta table and optionally apply Z-ordering
    
    Args:
        spark: SparkSession object
        path: Path to Delta table
        zorder_columns: Optional list of columns for Z-ordering
    """
    logger.info(f"Optimizing Delta table at {path}")
    
    if zorder_columns:
        spark.sql(f"OPTIMIZE delta.`{path}` ZORDER BY ({', '.join(zorder_columns)})")
        logger.info(f"Applied Z-ordering on columns: {zorder_columns}")
    else:
        spark.sql(f"OPTIMIZE delta.`{path}`")
    
    logger.info("Optimization complete")


def vacuum_delta_table(spark: SparkSession, path: str, retention_hours: int = 168) -> None:
    """
    Run VACUUM on Delta table to remove old files
    
    Args:
        spark: SparkSession object
        path: Path to Delta table
        retention_hours: Retention period in hours (default: 7 days)
    """
    logger.info(f"Running VACUUM on {path} with {retention_hours}h retention")
    spark.sql(f"VACUUM delta.`{path}` RETAIN {retention_hours} HOURS")
    logger.info("VACUUM complete")


def get_table_metrics(spark: SparkSession, path: str) -> Dict:
    """
    Get metrics about a Delta table
    
    Args:
        spark: SparkSession object
        path: Path to Delta table
        
    Returns:
        Dictionary with table metrics
    """
    df = spark.read.format("delta").load(path)
    delta_table = DeltaTable.forPath(spark, path)
    
    # Get history
    history_df = delta_table.history(1)
    
    metrics = {
        "total_records": df.count(),
        "num_files": history_df.select("numFiles").collect()[0][0] if history_df.count() > 0 else 0,
        "size_in_bytes": history_df.select("operationMetrics.numOutputBytes").collect()[0][0] if history_df.count() > 0 else 0,
        "num_columns": len(df.columns),
        "columns": df.columns,
    }
    
    logger.info(f"Table metrics: {metrics}")
    return metrics


def merge_incremental_data(
    spark: SparkSession,
    target_path: str,
    source_df: DataFrame,
    merge_keys: List[str],
    update_columns: Optional[List[str]] = None
) -> None:
    """
    Perform incremental merge (upsert) into Delta table
    
    Args:
        spark: SparkSession object
        target_path: Path to target Delta table
        source_df: Source DataFrame with new/updated data
        merge_keys: Columns to use for matching records
        update_columns: Optional list of columns to update (None = all)
    """
    target_table = DeltaTable.forPath(spark, target_path)
    
    # Build merge condition
    merge_condition = " AND ".join([f"target.{key} = source.{key}" for key in merge_keys])
    
    logger.info(f"Performing incremental merge on keys: {merge_keys}")
    logger.info(f"Merge condition: {merge_condition}")
    
    # Perform merge
    merge_builder = target_table.alias("target").merge(
        source_df.alias("source"),
        merge_condition
    )
    
    if update_columns:
        # Update only specified columns
        update_dict = {col: f"source.{col}" for col in update_columns}
        merge_builder = merge_builder.whenMatchedUpdate(set=update_dict)
    else:
        # Update all columns
        merge_builder = merge_builder.whenMatchedUpdateAll()
    
    merge_builder = merge_builder.whenNotMatchedInsertAll()
    
    merge_builder.execute()
    
    logger.info("Incremental merge complete")


def show_dataframe_summary(df: DataFrame, name: str = "DataFrame") -> None:
    """
    Display summary information about a DataFrame
    
    Args:
        df: DataFrame to summarize
        name: Name to display in logs
    """
    logger.info(f"=" * 70)
    logger.info(f"{name} Summary")
    logger.info(f"=" * 70)
    logger.info(f"Row count: {df.count():,}")
    logger.info(f"Column count: {len(df.columns)}")
    logger.info(f"Columns: {', '.join(df.columns)}")
    logger.info(f"Schema:")
    df.printSchema()
    logger.info(f"Sample data:")
    df.show(5, truncate=False)
    logger.info(f"=" * 70)


# Example usage
if __name__ == "__main__":
    # Create Spark session
    spark = create_spark_session("SparkUtils Test")
    
    # Create sample DataFrame
    data = [
        (1, "sensor_1", "2024-02-18 10:00:00", 25.5),
        (2, "sensor_2", "2024-02-18 10:01:00", 26.0),
    ]
    df = spark.createDataFrame(data, ["id", "sensor_id", "timestamp", "value"])
    
    # Show summary
    show_dataframe_summary(df, "Sample Data")
    
    # Add metadata
    df_with_metadata = add_ingestion_metadata(df)
    show_dataframe_summary(df_with_metadata, "With Metadata")
    
    spark.stop()
