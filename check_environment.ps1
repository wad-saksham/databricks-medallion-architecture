# Quick Environment Check Script
# Run this to diagnose installation issues

Write-Host "=" -ForegroundColor Cyan
Write-Host "ENVIRONMENT CHECK SCRIPT" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# Check 1: Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   Python NOT FOUND" -ForegroundColor Red
    Write-Host "   Install Python 3.9+ from https://www.python.org/" -ForegroundColor Red
}

# Check 2: Virtual Environment
Write-Host ""
Write-Host "2. Checking Virtual Environment..." -ForegroundColor Yellow
$venvPath = $null
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    $venvPath = ".\venv\Scripts\Activate.ps1"
} elseif (Test-Path ".\venv\bin\Activate.ps1") {
    $venvPath = ".\venv\bin\Activate.ps1"
}

if ($venvPath) {
    Write-Host "   Virtual environment exists" -ForegroundColor Green
    Write-Host "   Location: $venvPath" -ForegroundColor Cyan
    
    # Check if activated
    if ($env:VIRTUAL_ENV) {
        Write-Host "   Virtual environment is ACTIVATED" -ForegroundColor Green
    } else {
        Write-Host "   Virtual environment NOT activated" -ForegroundColor Yellow
        Write-Host "   Run: & '$venvPath'" -ForegroundColor Yellow
    }
} else {
    Write-Host "   Virtual environment NOT FOUND" -ForegroundColor Red
    Write-Host "   Run: python -m venv venv" -ForegroundColor Red
}

# Check 3: Java
Write-Host ""
Write-Host "3. Checking Java..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "   $javaVersion" -ForegroundColor Green
    
    if ($env:JAVA_HOME) {
        Write-Host "   JAVA_HOME: $env:JAVA_HOME" -ForegroundColor Green
    } else {
        Write-Host "   JAVA_HOME not set (may cause issues)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   Java NOT FOUND" -ForegroundColor Red
    Write-Host "   Install Java 11+ from https://www.oracle.com/java/technologies/downloads/" -ForegroundColor Red
}

# Check 4: Required Files
Write-Host ""
Write-Host "4. Checking Required Files..." -ForegroundColor Yellow

$requiredFiles = @(
    "requirements.txt",
    "requirements-minimal.txt",
    "databricks-medallion\src\__init__.py",
    "databricks-medallion\src\config\__init__.py",
    "databricks-medallion\src\utils\__init__.py",
    "databricks-medallion\src\quality\__init__.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   $file" -ForegroundColor Green
    } else {
        Write-Host "   $file MISSING" -ForegroundColor Red
    }
}

# Check 5: Python Packages (if venv is activated)
if ($env:VIRTUAL_ENV) {
    Write-Host ""
    Write-Host "5. Checking Python Packages..." -ForegroundColor Yellow
    
    $packages = @("pyspark", "delta-spark", "pandas", "numpy", "faker")
    
    foreach ($package in $packages) {
        try {
            $version = pip show $package 2>&1 | Select-String "Version:" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
            if ($version) {
                Write-Host "   $package : $version" -ForegroundColor Green
            } else {
                Write-Host "   $package NOT INSTALLED" -ForegroundColor Red
            }
        } catch {
            Write-Host "   $package NOT INSTALLED" -ForegroundColor Red
        }
    }
} else {
    Write-Host ""
    Write-Host "5. Python Packages Check SKIPPED (activate venv first)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "NEXT STEP: Create virtual environment" -ForegroundColor Yellow
    Write-Host "Run: python -m venv venv" -ForegroundColor White
    Write-Host ""
} elseif (-not $env:VIRTUAL_ENV) {
    Write-Host "NEXT STEP: Activate virtual environment" -ForegroundColor Yellow
    Write-Host "Run: .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "NEXT STEP: Install packages" -ForegroundColor Yellow
    Write-Host "Run: pip install -r requirements-minimal.txt" -ForegroundColor White
    Write-Host ""
}

Write-Host "For detailed troubleshooting, see: INSTALLATION_TROUBLESHOOTING.md" -ForegroundColor Cyan
Write-Host ""
