# Python 3.13 Compatibility Issue

## Problem

Your system is running **Python 3.13.2**, which is **not yet fully compatible** with Apache Spark/PySpark. 

The error you're seeing ("Python worker exited unexpectedly") occurs because:
- PySpark uses inter-process communication between the JVM (Java) and Python workers
- Python 3.13 introduced changes that break this communication
- As of February 2026, PySpark has limited support for Python 3.13

## Solution

**Use Python 3.11 or 3.12** instead of Python 3.13 for this project.

### Recommended: Install Python 3.11 or 3.12

1. **Download Python 3.11** or **3.12** from: https://www.python.org/downloads/

2. **Install Python 3.11/3.12** alongside your Python 3.13 installation
   - During installation, check "Add Python to PATH"
   - Note the installation directory

3. **Create a virtual environment** with the correct Python version:
   ```powershell
   # Use Python 3.11 or 3.12 executable
   C:\Path\To\Python311\python.exe -m venv .venv311
   
   # Activate the virtual environment
   .\.venv311\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Run your notebook** with the correct Python:
   ```powershell
   python databricks-medallion/notebooks/00_setup_environment.py
   ```

### Alternative: Use conda/miniconda

```bash
# Create environment with Python 3.11
conda create -n databricks-env python=3.11
conda activate databricks-env

# Install dependencies
pip install -r requirements.txt
```

## What Was Fixed

Even though Python 3.13 isn't fully compatible, the following improvements were made to your project:

1. ✅ **Updated PySpark** to version 3.5.8 (latest 3.5.x with best Python 3.13 support)
2. ✅ **Updated Delta Lake** to version 3.2.1
3. ✅ **Added Windows Hadoop support** - automatically downloads `winutils.exe`
4. ✅ **Enhanced configuration** - better Windows compatibility settings
5. ✅ **Added Python version warning** - alerts when using Python 3.13
6. ✅ **Explicit Python executable configuration** - helps Spark find the right Python

These improvements will make the project work smoothly once you switch to Python 3.11 or 3.12.

## Verification

After installing Python 3.11/3.12 and setting up the environment:

```powershell
python --version  # Should show 3.11.x or 3.12.x
python databricks-medallion/notebooks/00_setup_environment.py
```

You should see:
- ✅ Spark Session Created
- ✅ Spark Version: 3.5.8
- ✅ Basic Spark Test: Created DataFrame with 2 rows
- ✅ Delta Lake tests passing

## Additional Resources

- [PySpark Python Version Compatibility](https://spark.apache.org/docs/latest/)
- [Python Downloads](https://www.python.org/downloads/)
- [Conda Documentation](https://docs.conda.io/)
