# Check Python Versions Script
# This script helps you find and use a compatible Python version (3.11 or 3.12)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PYTHON VERSION CHECKER FOR PYSPARK" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check current Python version
Write-Host "Current Python Version:" -ForegroundColor Yellow
$pythonVersion = & python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor White

# Check if Python 3.13
if ($pythonVersion -match "3\.13") {
    Write-Host ""
    Write-Host "âš ï¸  WARNING: Python 3.13 is not fully compatible with PySpark!" -ForegroundColor Red
    Write-Host "   You need Python 3.11 or 3.12 for this project." -ForegroundColor Yellow
    Write-Host ""
}

# Search for other Python installations
Write-Host "Searching for Python installations on your system..." -ForegroundColor Yellow
Write-Host ""

$pythonVersions = @()

# Common installation paths
$searchPaths = @(
    "$env:LOCALAPPDATA\Programs\Python",
    "$env:ProgramFiles\Python*",
    "$env:ProgramFiles(x86)\Python*",
    "C:\Python*"
)

foreach ($path in $searchPaths) {
    $foundPaths = Get-ChildItem -Path $path -ErrorAction SilentlyContinue -Directory
    foreach ($dir in $foundPaths) {
        $pythonExe = Join-Path $dir.FullName "python.exe"
        if (Test-Path $pythonExe) {
            try {
                $version = & $pythonExe --version 2>&1
                if ($version -match "Python (3\.\d+\.\d+)") {
                    $pythonVersions += [PSCustomObject]@{
                        Version = $matches[1]
                        Path = $pythonExe
                        Compatible = $matches[1] -match "3\.(11|12)"
                    }
                }
            } catch {
                # Skip if unable to execute
            }
        }
    }
}

if ($pythonVersions.Count -eq 0) {
    Write-Host "No Python installations found in common locations." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ðŸ“¥ Please download Python 3.11 or 3.12 from:" -ForegroundColor Cyan
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor White
} else {
    Write-Host "Found Python installations:" -ForegroundColor Green
    Write-Host ""
    
    foreach ($py in $pythonVersions) {
        $status = if ($py.Compatible) { "âœ… COMPATIBLE" } else { "âŒ NOT COMPATIBLE" }
        $color = if ($py.Compatible) { "Green" } else { "Red" }
        Write-Host "  Python $($py.Version) - $status" -ForegroundColor $color
        Write-Host "    Path: $($py.Path)" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Find best compatible version
    $bestVersion = $pythonVersions | Where-Object { $_.Compatible } | Select-Object -First 1
    
    if ($bestVersion) {
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "RECOMMENDED ACTION" -ForegroundColor Cyan
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Use Python $($bestVersion.Version) for this project:" -ForegroundColor Green
        Write-Host ""
        Write-Host "1. Create a virtual environment:" -ForegroundColor Yellow
        Write-Host "   $($bestVersion.Path) -m venv .venv" -ForegroundColor White
        Write-Host ""
        Write-Host "2. Activate it:" -ForegroundColor Yellow
        Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host ""
        Write-Host "3. Install dependencies:" -ForegroundColor Yellow
        Write-Host "   pip install -r requirements.txt" -ForegroundColor White
        Write-Host ""
        Write-Host "4. Run the setup:" -ForegroundColor Yellow
        Write-Host "   python databricks-medallion\notebooks\00_setup_environment.py" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "ACTION REQUIRED" -ForegroundColor Cyan
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "No compatible Python version found." -ForegroundColor Red
        Write-Host ""
        Write-Host "ðŸ“¥ Please install Python 3.11 or 3.12:" -ForegroundColor Yellow
        Write-Host "   https://www.python.org/downloads/" -ForegroundColor White
        Write-Host ""
    }
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information, see: PYTHON_VERSION_ISSUE.md" -ForegroundColor Cyan
Write-Host ""

