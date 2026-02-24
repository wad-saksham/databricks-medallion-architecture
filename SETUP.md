# ⚙️ ENVIRONMENT SETUP GUIDE

## 📋 Prerequisites Checklist

### 1. Software Installation

#### Python 3.9+

```powershell
# Check if installed
python --version

# Download from: https://www.python.org/downloads/
# ✅ Make sure to check "Add Python to PATH" during installation
```

#### Git

```powershell
# Check if installed
git --version

# Download from: https://git-scm.com/downloads
```

#### VS Code

```powershell
# Download from: https://code.visualstudio.com/
```

#### Power BI Desktop (For Project 2)

```powershell
# Download from: https://aka.ms/pbidesktop
# Or get from Microsoft Store
```

---

## 🔧 Setup Instructions

### Step 1: Create Virtual Environment

```powershell
# Navigate to project directory
cd "c:\Users\saksh\OneDrive\Desktop\Data enginnering project"

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies

```powershell
# Make sure venv is activated (you should see (venv) in prompt)
pip install --upgrade pip

# Install core packages
pip install -r requirements.txt
```

### Step 3: Databricks Community Edition

1. Go to: https://community.cloud.databricks.com/
2. Click "Sign Up"
3. Fill in details (use personal email)
4. Verify email
5. Login → Create Cluster
   - Name: "dev-cluster"
   - Runtime: Latest LTS
   - Single node
6. Wait 3-5 minutes for cluster to start

**Save your workspace URL** (something like: https://community.cloud.databricks.com/?o=XXXXXX)

### Step 4: AWS Free Tier Setup

1. Go to: https://aws.amazon.com/free/
2. Create AWS account
3. Verify identity (credit card required but won't be charged)
4. Navigate to IAM → Create User
   - Name: `databricks-dev`
   - Access type: Programmatic access
   - Permissions: AmazonS3FullAccess (for learning only)
5. Download credentials CSV
6. **Keep credentials safe!**

### Step 5: Configure AWS Credentials

```powershell
# Install AWS CLI
# Download from: https://aws.amazon.com/cli/

# Configure credentials
aws configure
# Enter:
#   AWS Access Key ID: [from CSV]
#   AWS Secret Access Key: [from CSV]
#   Default region: us-east-1
#   Default output format: json

# Test
aws s3 ls
```

### Step 6: Create S3 Bucket

```powershell
# Create bucket (name must be globally unique)
aws s3 mb s3://your-name-data-engineering-demo

# Example:
aws s3 mb s3://saksh-data-engineering-demo
```

### Step 7: GitHub Repository Setup

```powershell
# Initialize git (if not already)
git init

# Create .gitignore
# (Already provided in project)

# First commit
git add .
git commit -m "Initial commit: Project structure and documentation"

# Create repo on GitHub.com
# Then link it:
git remote add origin https://github.com/YOUR_USERNAME/data-engineering-portfolio.git
git branch -M main
git push -u origin main
```

---

## 📦 Required Python Packages

**requirements.txt contents:**

```
# Core
pyspark==3.5.0
delta-spark==3.0.0
pandas==2.1.0
numpy==1.24.3

# Data Generation
faker==19.3.1

# AWS
boto3==1.28.25
botocore==1.31.25

# Data Quality
great-expectations==0.18.0

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1

# Testing
pytest==7.4.0
pytest-cov==4.1.0

# Linting
black==23.7.0
flake8==6.1.0

# Notebook support (optional)
jupyter==1.0.0
ipython==8.14.0
```

---

## 🗂️ Project Structure

```
Data enginnering project/
│
├── databricks-medallion/           # Project 1
│   ├── README.md
│   ├── notebooks/
│   │   ├── 01_bronze_layer.py
│   │   ├── 02_silver_layer.py
│   │   └── 03_gold_layer.py
│   ├── src/
│   │   ├── config/
│   │   ├── utils/
│   │   └── quality/
│   ├── data/
│   │   └── sample/
│   ├── tests/
│   └── docs/
│
├── retail-analytics/               # Project 2
│   ├── README.md
│   ├── notebooks/
│   ├── src/
│   │   ├── ingestion/
│   │   ├── transformation/
│   │   └── analytics/
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── sample/
│   ├── powerbi/
│   ├── sql/
│   └── tests/
│
├── venv/                          # Virtual environment
├── .gitignore
├── requirements.txt
├── README.md                      # Main portfolio README
├── MASTER_ROADMAP.md
├── LEARNING_GUIDE.md
└── SETUP.md                       # This file
```

---

## ✅ Verification Tests

### Test 1: Python Environment

```powershell
python -c "import pyspark; print(pyspark.__version__)"
# Should print: 3.5.0
```

### Test 2: AWS Connection

```powershell
aws s3 ls s3://your-bucket-name
# Should list (empty for now)
```

### Test 3: PySpark Local

```powershell
python
>>> from pyspark.sql import SparkSession
>>> spark = SparkSession.builder.appName("test").getOrCreate()
>>> df = spark.createDataFrame([(1, "test")], ["id", "value"])
>>> df.show()
# Should display a table
>>> exit()
```

---

## 🚨 Common Issues & Solutions

### Issue 1: PowerShell Script Execution Error

```
Error: "cannot be loaded because running scripts is disabled"

Solution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Java Not Found (PySpark)

```
Error: "JAVA_HOME is not set"

Solution:
# Download JDK 11: https://adoptium.net/
# Set environment variable:
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Eclipse Adoptium\jdk-11.0.x', 'Machine')
```

### Issue 3: Databricks Cluster Won't Start

```
Solution:
- Wait 5-10 minutes
- Try creating new cluster
- Check community edition limits (8 hours/day)
```

### Issue 4: AWS Credentials Not Working

```
Solution:
# Check credentials file
cat ~/.aws/credentials
# Should show:
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

---

## 🎯 Next Steps

Once setup is complete:

1. ✅ Review LEARNING_GUIDE.md
2. ✅ Review MASTER_ROADMAP.md
3. ✅ Start with Project 1: databricks-medallion/
4. ✅ Follow along with notebooks

---

## 📞 Need Help?

Common resources:

- PySpark Docs: https://spark.apache.org/docs/latest/api/python/
- Databricks Docs: https://docs.databricks.com/
- Delta Lake Docs: https://docs.delta.io/

---

**Setup complete? Let's start building! 🚀**
