# ============================================================
# OFFICE ASSISTANT AI - START ALL SERVICES
# ============================================================

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "       OFFICE ASSISTANT AI                   " -ForegroundColor Cyan
Write-Host "       Starting All Services                 " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# MCP SERVER DIRECTORY
# ============================================================

$MCP = Join-Path $ROOT "mcp-server"

# ============================================================
# START MCP SERVERS
# ============================================================

Write-Host "[1/8] Starting Weather MCP Server..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Set-Location '$MCP'; .\.venv\Scripts\Activate.ps1; python -m servers.Weather_Server"


Write-Host "[2/8] Starting Utility MCP Server..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Set-Location '$MCP'; .\.venv\Scripts\Activate.ps1; python -m servers.Utility_Server"


Write-Host "[3/8] Starting Communication MCP Server..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Set-Location '$MCP'; .\.venv\Scripts\Activate.ps1; python -m servers.Communication_Server"


Write-Host "[4/8] Starting Document MCP Server..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Set-Location '$MCP'; .\.venv\Scripts\Activate.ps1; python -m servers.Document_Server"


Write-Host "[5/8] Starting Database MCP Server..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Set-Location '$MCP'; .\.venv\Scripts\Activate.ps1; python -m servers.Database_Server"


Write-Host "[6/8] Starting Office MCP Server..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Set-Location '$MCP'; .\.venv\Scripts\Activate.ps1; python -m servers.Office_Server"


# ============================================================
# WAIT FOR MCP SERVERS
# ============================================================

Write-Host ""
Write-Host "Waiting for MCP servers to initialize..." -ForegroundColor Cyan

Start-Sleep -Seconds 5


# ============================================================
# START BACKEND
# ============================================================

$BACKEND = Join-Path $ROOT "backend"

Write-Host ""
Write-Host "[7/8] Starting FastAPI Backend..." -ForegroundColor Green

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Set-Location '$BACKEND'; .\.venv\Scripts\Activate.ps1; uvicorn app.api:app --reload --port 8080"


# ============================================================
# WAIT FOR BACKEND
# ============================================================

Write-Host ""
Write-Host "Waiting for backend to initialize..." -ForegroundColor Cyan

Start-Sleep -Seconds 5


# ============================================================
# START FRONTEND
# ============================================================

$FRONTEND = Join-Path $ROOT "frontend"

Write-Host ""
Write-Host "[8/8] Starting React Frontend..." -ForegroundColor Green

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Set-Location '$FRONTEND'; npm run dev"


# ============================================================
# COMPLETE
# ============================================================

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "       ALL SERVICES STARTED                  " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "MCP Servers : RUNNING" -ForegroundColor Green
Write-Host "Backend     : http://localhost:8080" -ForegroundColor Green
Write-Host "Frontend    : http://localhost:5173" -ForegroundColor Green

Write-Host ""
Write-Host "Open the frontend in your browser:" -ForegroundColor Yellow
Write-Host "http://localhost:5173" -ForegroundColor White

Write-Host ""