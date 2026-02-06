# Atlas Backend Deployment Script
param(
    [switch]$Dev = $false,
    [switch]$Prod = $false,
    [switch]$Install = $false
)

$ErrorActionPreference = "Continue"
$BackendDir = $PSScriptRoot

# Color functions
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Error-Custom { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }

Write-Info "Atlas Backend Deployment"
Write-Host "========================"
Write-Host ""

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Python not found. Install from https://www.python.org/"
    exit 1
}

$pythonVersion = python --version
Write-Success "Python: $pythonVersion"

# Create virtual environment if needed
if (-not (Test-Path "$BackendDir\venv")) {
    Write-Info "Creating virtual environment..."
    python -m venv "$BackendDir\venv"
    Write-Success "Virtual environment created"
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
& "$BackendDir\venv\Scripts\Activate.ps1"

# Install/update dependencies
if ($Install -or -not (Test-Path "$BackendDir\venv\Lib\site-packages\fastapi")) {
    Write-Info "Installing dependencies..."
    if (Test-Path "$BackendDir\requirements.txt") {
        pip install -r "$BackendDir\requirements.txt"
        Write-Success "Dependencies installed"
    }
    else {
        Write-Error-Custom "requirements.txt not found"
        exit 1
    }
}

# Create necessary directories
$dirs = @("data", "data\db", "logs")
foreach ($dir in $dirs) {
    $path = Join-Path $BackendDir $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Success "Created directory: $dir"
    }
}

# Create .env if needed
if (-not (Test-Path "$BackendDir\.env")) {
    if (Test-Path "$BackendDir\.env.example") {
        Copy-Item "$BackendDir\.env.example" "$BackendDir\.env"
        Write-Success "Created .env file"
    }
}

# Run backend
Write-Host ""
Write-Info "Starting Atlas Backend on port 8001..."
Write-Host ""

if ($Prod) {
    # Production mode
    Write-Info "Running in PRODUCTION mode"
    if (Get-Command uvicorn -ErrorAction SilentlyContinue) {
        uvicorn main_api:app --host 0.0.0.0 --port 8001 --workers 4
    }
    else {
        python main_api.py --port 8001
    }
}
else {
    # Development mode (default)
    Write-Info "Running in DEVELOPMENT mode"
    if (Test-Path "$BackendDir\main_api.py") {
        python main_api.py
    }
    elseif (Test-Path "$BackendDir\main.py") {
        python main.py
    }
    else {
        Write-Error-Custom "Main entry point not found (main_api.py or main.py)"
        exit 1
    }
}
