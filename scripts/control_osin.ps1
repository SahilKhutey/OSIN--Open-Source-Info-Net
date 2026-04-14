# OSIN Mission Control: Unified Launcher (PowerShell)
# Version: 1.0.0 (v12 Production Grade)

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("init", "start-infra", "start-app", "status", "stop")]
    $Action
)

$OSIN_ROOT = Get-Location
$BACKEND_DIR = Join-Path $OSIN_ROOT "backend"
$DASHBOARD_DIR = Join-Path $OSIN_ROOT "dashboard"

function Show-Header {
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "                OSIN MISSION CONTROL v12" -ForegroundColor Cyan
    Write-Host "          Global Intelligence Grid Orchestration" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Check-Depends {
    Write-Host "[*] Auditing Intelligence Environment..." -ForegroundColor Yellow
    
    # Python Check
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { Write-Host "[OK] Python detected: $($python.Version)" -ForegroundColor Green }
    else { Write-Host "[ERR] Python 3.9+ Mandatory" -ForegroundColor Red }

    # Npm Check
    $npm = Get-Command npm -ErrorAction SilentlyContinue
    if ($npm) { Write-Host "[OK] Npm detected" -ForegroundColor Green }
    else { Write-Host "[ERR] Node.js/Npm required for Dashboard" -ForegroundColor Red }

    # Docker Check
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if ($docker) { Write-Host "[OK] Docker detected (Infrastructure ready)" -ForegroundColor Green }
    else { 
        Write-Host "[WARN] Docker not in PATH. Full Infra (Kafka/Neo4j) will be simulated." -ForegroundColor Yellow 
        $env:OSIN_BLIND_MODE = "true"
    }

    # Kubectl Check
    $k8s = Get-Command kubectl -ErrorAction SilentlyContinue
    if ($k8s) { Write-Host "[OK] Kubernetes CLI detected (v12 Ready)" -ForegroundColor Green }
    else { Write-Host "[INFO] Kubectl missing. Targeted for local dev stack." -ForegroundColor Blue }
}

function Start-Infrastructure {
    Write-Host "[*] Orchestrating Data Ingestion Grid..." -ForegroundColor Yellow
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        Write-Host "Launching Docker Compose stack..."
        docker-compose up -d
    } else {
        Write-Host "[!] Docker Compose missing. Entering Simulation/Blind Mode." -ForegroundColor Cyan
        $env:OSIN_BLIND_MODE = "true"
    }
}

function Start-Application {
    Show-Header
    Write-Host "[*] Deploying Intelligence Interfaces..." -ForegroundColor Yellow

    # Start Backend in new window
    Write-Host "-> Launching FastAPI Backend (Port 8000)..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $BACKEND_DIR; `$env:OSIN_BLIND_MODE='true'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    
    # Start Dashboard in new window
    Write-Host "-> Launching Vite Dashboard (Port 5173)..."
    if (Test-Path (Join-Path $DASHBOARD_DIR "node_modules")) {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $DASHBOARD_DIR; npm run dev"
    } else {
        Write-Host "[!] Dashboard node_modules missing. Run '.\scripts\control_osin.ps1 init' first." -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Launch Sequence Initiated." -ForegroundColor Green
    Write-Host "Backup Health Monitor: http://localhost:8002/static" -ForegroundColor Gray
}

switch ($Action) {
    "init" { 
        Show-Header
        Check-Depends 
        Write-Host "[*] Initializing Frontend Dependencies (Force Legacy)..." -ForegroundColor Yellow
        Set-Location $DASHBOARD_DIR
        npm install --legacy-peer-deps
        Set-Location $OSIN_ROOT
    }
    "start-infra" { Start-Infrastructure }
    "start-app" { Start-Application }
    "status" {
        Write-Host "[*] Querying Intelligence Health..." -ForegroundColor Yellow
        try {
            $resp = Invoke-RestMethod -Uri "http://localhost:8000/"
            Write-Host "Global Status: $($resp.status)" -ForegroundColor Green
        } catch {
            Write-Host "Backend Connectivity: OFFLINE" -ForegroundColor Red
        }
    }
    "stop" {
        Write-Host "[*] Decommissioning Network..." -ForegroundColor Red
        Get-Process | Where-Object { $_.ProcessName -match "uvicorn" -or $_.ProcessName -match "node" } | Stop-Process -Force
    }
}
