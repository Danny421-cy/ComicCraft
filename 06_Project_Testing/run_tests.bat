@echo off
REM ===================================================================
REM ComicCraft — 1-Click Automated Test Suite Launcher
REM ===================================================================
echo ===================================================
echo  ComicCraft Automated Test Suite Execution
echo ===================================================

cd /d "%~dp0..\05_Project_Development"

if exist "..\.venv\Scripts\pytest.exe" (
    set "PYTEST_EXE=..\.venv\Scripts\pytest.exe"
) else (
    set "PYTEST_EXE=pytest"
)

echo Running 20-case test matrix verification...
%PYTEST_EXE% ..\06_Project_Testing\test_suite -v --tb=short

if %ERRORLEVEL% equ 0 (
    echo.
    echo ===================================================
    echo  [SUCCESS] All ComicCraft test cases PASSED (20/20)
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo  [WARNING] Some tests encountered issues.
    echo ===================================================
)

pause

