# 📚 DATA ENGINEERING LEARNING GUIDE

> Complete learning resource for mastering concepts used in these projects

---

## 🎯 TABLE OF CONTENTS

1. [Medallion Architecture](#medallion-architecture)
2. [Delta Lake](#delta-lake)
3. [Databricks Platform](#databricks-platform)
4. [PySpark Essentials](#pyspark-essentials)
5. [Dimensional Modeling](#dimensional-modeling)
6. [Data Quality](#data-quality)
7. [Cloud Storage Patterns](#cloud-storage-patterns)
8. [Interview Preparation](#interview-preparation)

---

## 🏅 MEDALLION ARCHITECTURE

### What is it?

A data design pattern that organizes data into three progressive layers:

- **Bronze (Raw)**: Data as-is from source
- **Silver (Refined)**: Cleaned and conformed
- **Gold (Curated)**: Business-ready aggregations

### Why use it?

**Benefits:**

1. **Clear separation of concerns** - Each layer has a distinct purpose
2. **Incremental processing** - Only process new/changed data
3. **Data lineage** - Track data from source to analytics
4. **Recovery** - Can rebuild downstream from upstream layers
5. **Multiple consumers** - Different teams can use different layers

### Real-World Example:

```
E-commerce Order Data Flow:

BRONZE Layer:
  orders_raw/
    - Raw JSON from website API
    - Includes duplicates, nulls, bad formats
    - Append-only (never delete source data)

SILVER Layer:
  orders_cleaned/
    - Deduplicated orders
    - Nulls handled
    - Standardized date formats
    - Validated against business rules

GOLD Layer:
  sales_by_region/
    - Pre-aggregated metrics
  customer_ltv/
    - Customer lifetime value
  product_performance/
    - SKU-level analytics
```

### When to Use Each Layer:

**Bronze** → Data engineers (troubleshooting, reprocessing)
**Silver** → Data scientists (feature engineering, ML)
**Gold** → Business analysts (dashboards, reports)

---

## 💎 DELTA LAKE

### What is Delta Lake?

Open-source storage layer that brings **ACID transactions** to data lakes.

Think of it as: **Parquet + Transaction Log + Time Travel**

### Key Concepts:

#### 1. ACID Transactions

```
Problem: Multiple jobs writing to same file → corruption
Solution: Delta ensures atomic writes (all or nothing)
```

#### 2. Schema Enforcement & Evolution

```python
# Schema Enforcement (by default)
df.write.mode("append").save("path")  # Fails if schema doesn't match

# Schema Evolution (when needed)
df.write
  .option("mergeSchema", "true")
  .mode("append")
  .save("path")
```

#### 3. Time Travel

```python
# Read data as it was yesterday
df = spark.read.format("delta").option("versionAsOf", 1).load("path")

# Or by timestamp
df = spark.read.format("delta")
  .option("timestampAsOf", "2024-01-01")
  .load("path")
```

#### 4. Upserts (MERGE)

```python
deltaTable = DeltaTable.forPath(spark, "target_path")

deltaTable.alias("target").merge(
    source.alias("source"),
    "target.id = source.id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

### Delta Lake vs Parquet

| Feature           | Parquet  | Delta Lake                 |
| ----------------- | -------- | -------------------------- |
| Format            | Columnar | Columnar + Transaction Log |
| ACID              | ❌       | ✅                         |
| Schema Evolution  | Manual   | Automatic                  |
| Time Travel       | ❌       | ✅                         |
| Updates/Deletes   | Hard     | Easy (MERGE)               |
| Concurrent Writes | Risky    | Safe                       |

### When to Use Delta Lake?

✅ **Use when:**

- Need ACID guarantees
- Frequent updates/deletes
- Multiple concurrent writers
- Audit trail needed
- Building data warehouse on lake

❌ **Might skip when:**

- Write-once, read-many workload
- Small datasets (<100GB)
- Cost is extreme constraint

---

## 🧱 DATABRICKS PLATFORM

### What is Databricks?

Unified analytics platform built on Apache Spark. Think of it as:
**Spark + Notebooks + Collaboration + MLflow + Delta Lake**

### Core Components:

#### 1. Workspace

- Notebooks (interactive coding)
- Jobs (scheduled pipelines)
- Clusters (compute resources)

#### 2. Databricks Clusters

```
Types:
- All-Purpose: Interactive development
- Job Clusters: Automated pipelines (cheaper)

Cluster Modes:
- Standard: Single user
- High Concurrency: Multi-user with isolation
```

#### 3. DBFS (Databricks File System)

```
Virtual filesystem that accesses:
- Local SSD
- Cloud storage (S3, Azure Blob, GCS)

Paths:
dbfs:/my-data/file.csv
/dbfs/my-data/file.csv (via shell)
```

#### 4. Unity Catalog (Data Governance)

```
Three-level namespace:
catalog.schema.table

Example:
production.sales.customers
dev.test.sample_data
```

### Databricks Community Edition (Free)

**What you get:**

- ✅ 15GB RAM cluster
- ✅ Notebooks
- ✅ Delta Lake
- ✅ Spark 3.x
- ✅ Limited libraries

**Limitations:**

- ⏱️ Cluster auto-terminates after 2 hours
- 👤 Single user only
- 📦 No jobs/scheduling
- 🔒 No Unity Catalog

**Perfect for:** Learning, portfolios, small projects

---

## ⚡ PYSPARK ESSENTIALS

### Core Concepts

#### 1. DataFrames vs RDDs

```python
# RDD (old way) - low level
rdd = sc.parallelize([1, 2, 3])

# DataFrame (new way) - high level, optimized
df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "name"])
```

**Use DataFrames** - They're faster and easier

#### 2. Transformations vs Actions

**Transformations** (lazy - nothing happens yet):

```python
df.filter()
df.select()
df.groupBy()
df.join()
```

**Actions** (trigger computation):

```python
df.show()
df.count()
df.write.save()
df.collect()  # ⚠️ Be careful with large data!
```

### Essential PySpark Patterns

#### Reading Data

```python
# CSV
df = spark.read.csv("path", header=True, inferSchema=True)

# JSON
df = spark.read.json("path")

# Delta
df = spark.read.format("delta").load("path")

# Parquet
df = spark.read.parquet("path")
```

#### Common Transformations

```python
# Select columns
df.select("col1", "col2")

# Filter rows
df.filter(df.age > 25)
df.where("age > 25")  # Same thing

# Add column
df.withColumn("new_col", df.old_col * 2)

# Rename
df.withColumnRenamed("old", "new")

# Drop
df.drop("col1")

# Deduplicate
df.dropDuplicates(["key_col"])
```

#### Joins

```python
# Inner join (default)
df1.join(df2, on="id", how="inner")

# Left join
df1.join(df2, on="id", how="left")

# Complex join condition
df1.join(df2, (df1.id == df2.id) & (df1.type == df2.type))
```

#### Aggregations

```python
from pyspark.sql import functions as F

# Group by
df.groupBy("category").agg(
    F.sum("sales").alias("total_sales"),
    F.avg("price").alias("avg_price"),
    F.count("*").alias("count")
)

# Window functions
from pyspark.sql.window import Window

window = Window.partitionBy("category").orderBy("date")
df.withColumn("running_total", F.sum("sales").over(window))
```

### Performance Tips

1. **Avoid collect()** on large data

```python
# ❌ Bad - brings all data to driver
data = df.collect()

# ✅ Good - process in cluster
df.write.save()
```

2. **Use broadcast for small tables**

```python
from pyspark.sql.functions import broadcast

# If dim_table is small (<100MB)
fact.join(broadcast(dim), "key")
```

3. **Partition your data**

```python
df.write.partitionBy("year", "month").save("path")
```

4. **Cache when reusing**

```python
df = df.cache()  # Keeps in memory
# Use df multiple times
```

---

## 🎲 DIMENSIONAL MODELING

### Star Schema 101

#### What is it?

A database schema with:

- **1 Fact Table** (center) - Metrics/measurements
- **N Dimension Tables** (points) - Descriptive context

```
        DimProduct
             |
             |
DimStore -- FactSales -- DimDate
             |
             |
        DimCustomer
```

### Fact Tables

**Characteristics:**

- Contain measurements (sales_amount, quantity, etc.)
- Large (millions to billions of rows)
- Foreign keys to dimensions
- Sometimes have degenerate dimensions (order_number)

**Example: FactSales**

```
fact_sales
├── sale_id (PK)
├── product_key (FK)
├── store_key (FK)
├── date_key (FK)
├── customer_key (FK)
├── quantity
├── unit_price
├── total_amount
└── cost_amount
```

**Types of Facts:**

1. **Additive** - Can sum across all dimensions (sales_amount)
2. **Semi-additive** - Can't sum across time (inventory_level)
3. **Non-additive** - Can't sum (ratios, percentages)

### Dimension Tables

**Characteristics:**

- Contain descriptive attributes
- Smaller (thousands to millions of rows)
- Denormalized (repeated data is OK)
- Surrogate keys (not natural keys)

**Example: DimProduct**

```
dim_product
├── product_key (PK - surrogate)
├── product_id (natural key)
├── product_name
├── category
├── subcategory
├── brand
├── supplier
├── unit_cost
├── effective_date
└── is_current
```

### Surrogate Keys

**Why use them?**

```
Natural Key: product_id = "ABC-123"
  Problems:
  - Can change over time
  - May not be unique across sources
  - Often composite (multiple columns)

Surrogate Key: product_key = 1001
  Benefits:
  - Never changes
  - Single column
  - Smaller size (better join performance)
  - Handles slowly changing dimensions
```

### Slowly Changing Dimensions (SCD)

#### Type 1 - Overwrite

```
Product "iPhone" changes price from $999 to $899
→ Just update the record (lose history)
```

#### Type 2 - Add New Row (Most Common)

```
product_key | product_id | price | effective_date | end_date   | is_current
------------|------------|-------|----------------|------------|------------
1001        | iPhone15   | 999   | 2023-01-01     | 2024-01-01 | N
1002        | iPhone15   | 899   | 2024-01-01     | 9999-12-31 | Y
```

#### Type 3 - Add New Column

```
product_id | price_current | price_previous
-----------|---------------|---------------
iPhone15   | 899           | 999
```

### Star vs Snowflake Schema

**Star Schema** (Recommended):

```
✅ Denormalized dimensions
✅ Faster queries (fewer joins)
✅ Simpler for analysts
```

**Snowflake Schema**:

```
✅ Normalized dimensions
✅ Saves storage space
❌ More complex queries
❌ Slower (more joins)
```

**For analytics projects**: Use Star Schema

---

## ✅ DATA QUALITY

### The Six Dimensions of Data Quality

1. **Accuracy** - Is the data correct?
2. **Completeness** - Are values missing?
3. **Consistency** - Does data match across sources?
4. **Timeliness** - Is data current?
5. **Validity** - Does data conform to rules?
6. **Uniqueness** - Are there duplicates?

### Common Data Quality Checks

```python
# 1. Null checks
df.filter(col("important_field").isNull()).count()

# 2. Duplicate checks
df.groupBy("key_field").count().filter("count > 1")

# 3. Range validation
df.filter((col("age") < 0) | (col("age") > 120))

# 4. Format validation
df.filter(~col("email").rlike(r'^[\w\.-]+@[\w\.-]+\.\w+$'))

# 5. Referential integrity
fact.join(dim, "key", "left_anti")  # Find orphan records

# 6. Business rules
df.filter(col("order_total") != col("quantity") * col("unit_price"))
```

### Data Quality Framework Pattern

```python
class DataQualityCheck:
    def __init__(self, name, check_function, threshold):
        self.name = name
        self.check_fn = check_function
        self.threshold = threshold

    def run(self, df):
        result = self.check_fn(df)
        passed = result <= self.threshold
        return {
            "check": self.name,
            "result": result,
            "threshold": self.threshold,
            "passed": passed
        }

# Usage
checks = [
    DataQualityCheck(
        "Null Rate - Email",
        lambda df: df.filter(col("email").isNull()).count() / df.count(),
        threshold=0.05  # Max 5% nulls
    ),
    DataQualityCheck(
        "Duplicate Orders",
        lambda df: df.groupBy("order_id").count().filter("count > 1").count(),
        threshold=0  # No duplicates allowed
    )
]
```

---

## ☁️ CLOUD STORAGE PATTERNS

### Storage Hierarchy

```
Storage Account / S3 Bucket
├── Container / Bucket
    ├── folder/
        ├── year=2024/
            ├── month=01/
                ├── day=15/
                    └── data.parquet
```

### Partitioning Strategies

**Time-based** (Most common):

```
data/
├── year=2024/
│   ├── month=01/
│   │   ├── day=01/
│   │   ├── day=02/
```

**Categorical**:

```
sales/
├── region=north/
│   ├── data.parquet
├── region=south/
│   ├── data.parquet
```

**Hybrid**:

```
orders/
├── year=2024/
    ├── month=01/
        ├── status=completed/
        ├── status=pending/
```

### File Formats Comparison

| Format  | Use Case              | Pros                 | Cons                |
| ------- | --------------------- | -------------------- | ------------------- |
| CSV     | Exchange, simple data | Human-readable       | No schema, slow     |
| JSON    | Semi-structured       | Flexible, nested     | Verbose, slow       |
| Parquet | Analytics             | Columnar, compressed | Not human-readable  |
| Delta   | Data warehouse        | ACID, time travel    | Requires Delta Lake |

---

## 🎤 INTERVIEW PREPARATION

### Key Talking Points

#### 1. Explain Medallion Architecture

```
"I implemented a three-layer architecture where Bronze stores raw data
for audit and reprocessing, Silver applies business rules and quality
checks for clean data, and Gold provides aggregated, analytics-ready
datasets. This pattern enables incremental processing, clear data lineage,
and serves multiple personas from data engineers to business analysts."
```

#### 2. Why Delta Lake?

```
"I chose Delta Lake for ACID transaction guarantees, which prevents
data corruption during concurrent writes. Features like schema evolution
and time travel were crucial for maintaining data quality and enabling
easy debugging. The MERGE operation simplified implementing slowly
changing dimensions."
```

#### 3. PySpark Optimizations

```
"I optimized performance through partitioning strategy, broadcast joins
for small dimension tables, and caching frequently accessed datasets. I
also used predicate pushdown to filter data early and minimize data
movement across the cluster."
```

#### 4. Data Quality Approach

```
"I implemented a multi-layered quality framework: schema validation at
ingestion, business rule checks during transformation, and aggregate
reconciliation in the gold layer. All checks are logged and trigger
alerts when thresholds are breached."
```

### Common Interview Questions

**Q: What's the difference between batch and streaming?**

```
Batch: Process bounded data at intervals (hourly, daily)
  - Lower cost
  - Simpler logic
  - Higher latency

Streaming: Process unbounded data continuously
  - Real-time insights
  - Event-driven
  - More complex
```

**Q: How do you handle late-arriving data?**

```
With watermarks and windows:
- Set watermark (e.g., 1 hour)
- Process data within watermark
- Store late data separately or reject
```

**Q: Explain slowly changing dimensions**

```
Type 1: Overwrite (no history)
Type 2: New row (full history) ← Most common
Type 3: New column (previous value only)
```

**Q: How do you ensure data quality?**

```
1. Input validation (schema, format)
2. Business rule checks (referential integrity)
3. Statistical checks (outliers)
4. Automated testing in CI/CD
5. Data observability (monitoring trends)
```

---

## 🎯 ACTION ITEMS

After reviewing this guide:

1. ✅ Set up Databricks Community Edition
2. ✅ Practice basic PySpark commands
3. ✅ Draw out a star schema on paper
4. ✅ Write 3 data quality checks
5. ✅ Explain Medallion Architecture in your own words

---

**Ready to apply this knowledge? Let's build! 🚀**
