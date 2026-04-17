# ============================================================
# Smart Manufacturing - Start All Services
# ============================================================
# Runs Flask backend (port 5000) + React Dashboard (port 5173)
# Usage: Right-click -> Run with PowerShell  OR  .\start.ps1
# ============================================================

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Smart Manufacturing - Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Flask Backend ---
Write-Host "[1/2] Starting Flask backend on http://localhost:5000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ROOT'; Write-Host 'Activating venv...' -ForegroundColor Green; .\.venv\Scripts\Activate.ps1; Write-Host 'Starting Flask...' -ForegroundColor Green; python application.py"
) -WindowStyle Normal

Start-Sleep -Seconds 2   # give Flask a moment to start

# --- React Dashboard ---
Write-Host "[2/2] Starting React Dashboard on http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ROOT\Dashboard'; Write-Host 'Starting Vite dev server...' -ForegroundColor Green; npm run dev"
) -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Both services launched!" -ForegroundColor Green
Write-Host "  Flask  -> http://localhost:5000" -ForegroundColor Green
Write-Host "  Dashboard -> http://localhost:5173" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
