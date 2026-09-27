# ===================================================================
# ComicCraft -- 1-Click Windows PowerShell Launcher
# Delegates to Phase 5: 05_Project_Development
# ===================================================================

$Host.UI.RawUI.WindowTitle = "ComicCraft -- AI Comic Story Creator"

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "            COMICCRAFT -- AI COMIC STORY CREATOR" -ForegroundColor Yellow
Write-Host "         Dual-LLM (Gemini) + Diffusion (Hugging Face)" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$devDir = Join-Path $rootDir "05_Project_Development"
$venvDir = Join-Path $rootDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

Set-Location $devDir

# Check virtual environment
if (-not (Test-Path $venvPython)) {
    Write-Host "[SETUP] Virtual environment not detected at $venvDir" -ForegroundColor Yellow
    Write-Host "[SETUP] Creating Python virtual environment..." -ForegroundColor White
    python -m venv $venvDir
    Write-Host "[SETUP] Installing requirements into virtual environment..." -ForegroundColor White
    $venvPip = Join-Path $venvDir "Scripts\pip.exe"
    & $venvPip install -r (Join-Path $devDir "requirements.txt")
    Write-Host "[SETUP] Environment ready!`n" -ForegroundColor Green
}

# Check for .env file
$envFile = Join-Path $devDir ".env"
$envExample = Join-Path $devDir ".env.example"
if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Write-Host "[NOTICE] .env not found. Creating from .env.example..." -ForegroundColor Yellow
        Copy-Item $envExample $envFile
    }
}

Write-Host "[LAUNCH] Starting FastAPI Uvicorn Server on http://127.0.0.1:8000..." -ForegroundColor Green
Write-Host "[INFO] Web Interface    : " -NoNewline; Write-Host "http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "[INFO] Interactive Docs : " -NoNewline; Write-Host "http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "[INFO] Diagnostic Lab   : " -NoNewline; Write-Host "http://127.0.0.1:8000/test-image" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to terminate the server.`n" -ForegroundColor Gray

# Open default browser after short pause in background
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
} | Out-Null

# Run Uvicorn
& $venvPython -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
