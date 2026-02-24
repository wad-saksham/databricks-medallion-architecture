# RUN_PROJECT.ps1 - Simple script to run all notebooks with correct Python

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MEDALLION ARCHITECTURE - PROJECT RUNNER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Try to find Python 3.12
$python312Paths = @(
    "C:\Python312\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\msys64\ucrt64\bin\python3.12.exe",
    "python3.12"
)

$pythonExe = $null
foreach ($path in $python312Paths) {
    if (Test-Path $path -ErrorAction SilentlyContinue) {
        $pythonExe = $path
        break
    }
}

# If no Python 3.12 found, try python3.12 command
if (-not $pythonExe) {
    try {
        $version = & python3.12 --version 2>&1
        if ($version -match "3.12") {
            $pythonExe = "python3.12"
        }
    } catch {}
}

if (-not $pythonExe) {
    Write-Host "❌ Python 3.12 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python 3.13 is NOT compatible with PySpark 4.1.1" -ForegroundColor Yellow
    Write-Host "Please install Python 3.12 from: https://www.python.org/downloads/release/python-3120/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Current Python detected:" -ForegroundColor Cyan
    python --version
    exit 1
}

Write-Host "✅ Using Python: $pythonExe" -ForegroundColor Green
& $pythonExe --version
Write-Host ""

# Check if packages are installed
Write-Host "[1/5] Checking packages..." -ForegroundColor Yellow
$checkCmd = "import pyspark, delta, pandas, faker, numpy; print('OK')"
$result = & $pythonExe -c $checkCmd 2>&1

if ($result -notmatch "OK") {
    Write-Host "   ⚠️  Packages not installed" -ForegroundColor Yellow
    Write-Host "   Installing packages..." -ForegroundColor Cyan
    & $pythonExe -m pip install pyspark delta-spark pandas numpy faker --quiet
    Write-Host "   ✅ Packages installed"  -ForegroundColor Green
} else {
    Write-Host "   ✅ All packages ready" -ForegroundColor Green
}
Write-Host ""

# Run notebooks
cd 'C:\Users\saksh\OneDrive\Desktop\Data enginnering project\databricks-medallion'

Write-Host "[2/5] Running 00_setup_environment.py..." -ForegroundColor Yellow
& $pythonExe notebooks\00_setup_environment.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Setup failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "[3/5] Running 01_bronze_layer.py..." -ForegroundColor Yellow
& $pythonExe notebooks\01_bronze_layer.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Bronze layer failed!" -ForegroundColor Red
   exit 1
}
Write-Host ""

Write-Host "[4/5] Running 02_silver_layer.py..." -ForegroundColor Yellow
& $pythonExe notebooks\02_silver_layer.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Silver layer failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "[5/5] Running 03_gold_layer.py..." -ForegroundColor Yellow
& $pythonExe notebooks\03_gold_layer.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Gold layer failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ ALL NOTEBOOKS COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Data generated in:" -ForegroundColor Cyan
Write-Host "  - data/bronze" -ForegroundColor White
Write-Host "  - data/silver" -ForegroundColor White
Write-Host "  - data/gold" -ForegroundColor White
