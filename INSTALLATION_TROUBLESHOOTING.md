# INSTALLATION TROUBLESHOOTING GUIDE

This guide helps you resolve common installation issues.

---

## FIXED ISSUES ✅

### 1. Missing `src/__init__.py` file

**Problem:** ImportError when running notebooks  
**Solution:** ✅ FIXED - Created `src/__init__.py` file

### 2. Updated requirements.txt

**Problem:** Missing py4j dependency for PySpark  
**Solution:** ✅ FIXED - Added py4j==0.10.9.7 to requirements.txt

---

## INSTALLATION OPTIONS

### Option 1: Minimal Installation (RECOMMENDED for first run)

Install only essential packages:

```powershell
pip install -r requirements-minimal.txt
```

This installs:

- pyspark==3.5.0
- delta-spark==3.0.0
- pandas==2.1.0
- numpy==1.24.3
- faker==19.3.1
- py4j==0.10.9.7

### Option 2: Full Installation

Install all packages including optional ones:

```powershell
pip install -r requirements.txt
```

---

## COMMON ISSUES & SOLUTIONS

### Issue 1: Java Not Found

**Error:** `JAVA_HOME is not set` or `Java command not found`

**Solution:**

1. Install Java 11 or later:

   ```powershell
   # Download from: https://www.oracle.com/java/technologies/downloads/
   # OR install via Chocolatey:
   choco install openjdk11
   ```

2. Set JAVA_HOME:

   ```powershell
   # Check Java installation
   java -version

   # Find Java path (usually in C:\Program Files\Java\...)
   # Set environment variable
   [System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Java\jdk-11', 'User')

   # Restart PowerShell
   ```

### Issue 2: Permission Denied (Execution Policy)

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: pip install fails

**Error:** `error: Microsoft Visual C++ 14.0 or greater is required`

**Solution:**

```powershell
# Option 1: Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/

# Option 2: Use prebuilt wheels
pip install --only-binary :all: pyspark delta-spark pandas numpy
```

### Issue 4: Import Error - "No module named 'pyspark'"

**Error:** `ModuleNotFoundError: No module named 'pyspark'`

**Solution:**

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Verify pip is from venv
pip --version
# Should show: ...venv\Scripts\pip.exe

# Reinstall
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

### Issue 5: Delta Spark Configuration Error

**Error:** `java.lang.ClassNotFoundException: io.delta.sql.DeltaSparkSessionExtension`

**Solution:**
This is fixed by ensuring delta-spark 3.0.0 is installed and matches PySpark 3.5.0:

```powershell
pip uninstall delta-spark pyspark
pip install pyspark==3.5.0 delta-spark==3.0.0
```

### Issue 6: Import Error - "No module named 'src'"

**Error:** `ModuleNotFoundError: No module named 'src'` or `No module named 'src.config'`

**Solution:** ✅ FIXED - Created `src/__init__.py` file
If still having issues:

```powershell
# Make sure you're in the databricks-medallion folder when running
cd databricks-medallion
python notebooks/00_setup_environment.py
```

### Issue 7: Faker Import Error

**Error:** `ModuleNotFoundError: No module named 'faker'`

**Solution:**

```powershell
pip install faker==19.3.1
```

### Issue 8: Memory Error during Spark operations

**Error:** `OutOfMemoryError: Java heap space`

**Solution:**
Add these environment variables:

```powershell
$env:PYSPARK_SUBMIT_ARGS = '--driver-memory 4g pyspark-shell'
```

Or edit `src/config/config.py` and increase memory:

```python
SPARK_CONFIG = {
    "spark.driver.memory": "4g",
    "spark.executor.memory": "4g",
}
```

---

## VERIFICATION STEPS

After installation, verify everything works:

### Step 1: Check Python & Virtual Environment

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Check Python
python --version
# Should show: Python 3.9+ or later

# Check pip
pip --version
# Should show path to venv
```

### Step 2: Check Java

```powershell
java -version
# Should show: java version "11" or later
```

### Step 3: Test PySpark Installation

```powershell
python -c "import pyspark; print(pyspark.__version__)"
# Should show: 3.5.0

python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.master('local[*]').appName('test').getOrCreate(); print('Spark OK')"
# Should show: Spark OK
```

### Step 4: Test Delta Lake

```powershell
python -c "import delta; print('Delta OK')"
# Should show: Delta OK
```

### Step 5: Test Project Imports

```powershell
cd databricks-medallion
python -c "from src.config import config; print('Config OK')"
# Should show: Config OK

python -c "from src.utils.data_generator import IoTDataGenerator; print('Data Generator OK')"
# Should show: Data Generator OK
```

### Step 6: Run Setup Notebook

```powershell
cd databricks-medallion
python notebooks/00_setup_environment.py
# Should complete without errors
```

---

## CLEAN INSTALL (if all else fails)

Start fresh with these steps:

```powershell
# 1. Delete virtual environment
Remove-Item -Recurse -Force venv

# 2. Delete any cached packages
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force databricks-medallion\src\__pycache__
Remove-Item -Recurse -Force databricks-medallion\src\*\__pycache__

# 3. Create new virtual environment
python -m venv venv

# 4. Activate
.\venv\Scripts\Activate.ps1

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Install minimal requirements
pip install -r requirements-minimal.txt

# 7. Verify
python -c "import pyspark, delta, pandas, faker; print('All packages OK')"

# 8. Run setup
cd databricks-medallion
python notebooks/00_setup_environment.py
```

---

## STILL HAVING ISSUES?

### Check System Requirements

- ✅ Python 3.9 or later
- ✅ Java 11 or later (Java 8 minimum)
- ✅ 8GB RAM minimum (16GB recommended)
- ✅ 2GB free disk space
- ✅ Windows 10/11 with PowerShell 5.1+

### Get Detailed Error Information

```powershell
# Run with verbose output
python notebooks/00_setup_environment.py 2>&1 | Tee-Object -FilePath error_log.txt

# Check the error_log.txt file for details
```

### Contact Information

If you encounter an error not listed here:

1. Copy the full error message
2. Note which step failed
3. Check Python and package versions
4. Review the error_log.txt file

---

## QUICK REFERENCE

### Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Deactivate Virtual Environment

```powershell
deactivate
```

### Update All Packages

```powershell
pip install --upgrade -r requirements-minimal.txt
```

### Check Installed Packages

```powershell
pip list
```

### Check PySpark Configuration

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
print(spark.sparkContext.getConf().getAll())
```

---

**Last Updated:** 2026-02-18  
**Status:** Ready to use ✅
