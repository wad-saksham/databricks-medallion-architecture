# Simple Installation Script for Data Engineering Project
# This script handles the complete setup process

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DATA ENGINEERING PROJECT - QUICK SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVer = python --version 2>&1
    Write-Host "   ✅ $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python not found!" -ForegroundColor Red
    Write-Host "   Install from: https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Step 2: Check/Create Virtual Environment
Write-Host ""
Write-Host "[2/6] Setting up Virtual Environment..." -ForegroundColor Yellow

$venvActivate = $null
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    $venvActivate = ".\venv\Scripts\Activate.ps1"
    Write-Host "   ✅ Virtual environment exists (Scripts)" -ForegroundColor Green
} elseif (Test-Path ".\venv\bin\Activate.ps1") {
    $venvActivate = ".\venv\bin\Activate.ps1"
    Write-Host "   ✅ Virtual environment exists (bin)" -ForegroundColor Green
} else {
    Write-Host "   Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        $venvActivate = ".\venv\Scripts\Activate.ps1"
    } elseif (Test-Path ".\venv\bin\Activate.ps1") {
        $venvActivate = ".\venv\bin\Activate.ps1"
    }
    
    if ($venvActivate) {
        Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Activate Virtual Environment
Write-Host ""
Write-Host "[3/6] Activating Virtual Environment..." -ForegroundColor Yellow
try {
    & $venvActivate
    Write-Host "   ✅ Activated: $venvActivate" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to activate" -ForegroundColor Red
    Write-Host "   Manually run: & '$venvActivate'" -ForegroundColor Yellow
    exit 1
}

# Step 4: Upgrade pip
Write-Host ""
Write-Host "[4/6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "   ✅ pip upgraded" -ForegroundColor Green

# Step 5: Install Packages (one by one for better success rate)
Write-Host ""
Write-Host "[5/6] Installing Python Packages..." -ForegroundColor Yellow
Write-Host "   This may take 5-10 minutes..." -ForegroundColor Cyan
Write-Host ""

$packages = @(
    @{name="py4j"; version="latest"},
    @{name="pyspark"; version="latest"},
    @{name="numpy"; version="latest"},
    @{name="pandas"; version="latest"},
    @{name="delta-spark"; version="latest"},
    @{name="faker"; version="latest"}
)

$successCount = 0
$failedPackages = @()

foreach ($pkg in $packages) {
    Write-Host "   Installing $($pkg.name)..." -ForegroundColor Cyan
    try {
        $output = python -m pip install $pkg.name 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $($pkg.name) installed" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "   ⚠️  $($pkg.name) - issues detected" -ForegroundColor Yellow
            $failedPackages += $pkg.name
        }
    } catch {
        Write-Host "   ❌ $($pkg.name) failed" -ForegroundColor Red
        $failedPackages += $pkg.name
    }
}

Write-Host ""
Write-Host "   Installed: $successCount / $($packages.Count) packages" -ForegroundColor $(if ($successCount -eq $packages.Count) { "Green" } else { "Yellow" })

if ($failedPackages.Count -gt 0) {
    Write-Host "   Failed packages: $($failedPackages -join ', ')" -ForegroundColor Yellow
}

# Step 6: Verify Installation
Write-Host ""
Write-Host "[6/6] Verifying Installation..." -ForegroundColor Yellow

$testScript = @"
try:
    import pyspark
    import delta
    import pandas
    import faker
    import numpy
    print('SUCCESS')
    print(f'PySpark: {pyspark.__version__}')
    print(f'Delta: {delta.__version__}')
    print(f'Pandas: {pandas.__version__}')
    print(f'Faker: {faker.__version__}')
    print(f'NumPy: {numpy.__version__}')
except Exception as e:
    print(f'ERROR: {e}')
"@

$result = python -c $testScript 2>&1
if ($result -match "SUCCESS") {
    Write-Host "   ✅ All core packages working!" -ForegroundColor Green
    Write-Host ""
    $result | ForEach-Object { if ($_ -notmatch "SUCCESS") { Write-Host "     $_" -ForegroundColor Cyan } }
} else {
    Write-Host "   ⚠️  Some packages may not be working" -ForegroundColor Yellow
    Write-Host "   Error: $result" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($result -match "SUCCESS") {
    Write-Host "✅ Ready to run the project!" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. cd databricks-medallion" -ForegroundColor White
    Write-Host "2. python notebooks/00_setup_environment.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  Installation completed with warnings" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "TROUBLESHOOTING:" -ForegroundColor Yellow
    Write-Host "1. Try running: pip list" -ForegroundColor White
    Write-Host "2. Check: INSTALLATION_TROUBLESHOOTING.md" -ForegroundColor White
    Write-Host "3. Try manual install: pip install pyspark delta-spark pandas faker" -ForegroundColor White
    Write-Host ""
}
