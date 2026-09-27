# ===================================================================
# ComicCraft -- PowerShell Automated Test Suite Runner
# ===================================================================
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " ComicCraft Automated Test Suite Execution" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDevDir = Join-Path (Split-Path -Parent $scriptDir) "05_Project_Development"
$venvPytest = Join-Path (Split-Path -Parent $scriptDir) ".venv\Scripts\pytest.exe"
$testSuiteDir = Join-Path $scriptDir "test_suite"

Set-Location $projectDevDir

if (Test-Path $venvPytest) {
    Write-Host "Executing tests with virtual environment pytest..." -ForegroundColor Green
    & $venvPytest $testSuiteDir -v --tb=short
} else {
    Write-Host "Executing tests with system pytest..." -ForegroundColor Yellow
    pytest $testSuiteDir -v --tb=short
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n===================================================" -ForegroundColor Green
    Write-Host " [SUCCESS] All ComicCraft test cases PASSED (20/20)" -ForegroundColor Green
    Write-Host "===================================================" -ForegroundColor Green
} else {
    Write-Host "`n[FAIL] Test suite reported failures." -ForegroundColor Red
}
