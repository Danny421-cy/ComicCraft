@echo off
REM ===================================================================
REM ComicCraft -- 1-Click Windows Batch Launcher
REM Delegates to Phase 5: 05_Project_Development
REM ===================================================================
title ComicCraft -- AI Comic Story Creator

echo ===================================================================
echo             COMICCRAFT -- AI COMIC STORY CREATOR
echo           Dual-LLM (Gemini) + Diffusion (Hugging Face)
echo ===================================================================
echo.

cd /d "%~dp005_Project_Development"

REM Check for virtual environment in root or local
set "VENV_DIR=%~dp0.venv"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [SETUP] Virtual environment not detected at %VENV_DIR%
    echo [SETUP] Creating Python virtual environment...
    python -m venv "%VENV_DIR%"
    echo [SETUP] Installing requirements...
    "%VENV_DIR%\Scripts\pip.exe" install -r requirements.txt
    echo [SETUP] Environment configured successfully!
    echo.
)

REM Check if .env exists, if not copy from .env.example
if not exist ".env" (
    if exist ".env.example" (
        echo [NOTICE] .env not found. Creating from .env.example...
        copy ".env.example" ".env" >nul
        echo [NOTICE] Created default .env file in 05_Project_Development.
        echo.
    )
)

echo [LAUNCH] Starting FastAPI Uvicorn Server...
echo [INFO] Web Application : http://127.0.0.1:8000
echo [INFO] Interactive Docs : http://127.0.0.1:8000/docs
echo [INFO] Diagnostic Lab   : http://127.0.0.1:8000/test-image
echo.
echo Press Ctrl+C in this terminal window to stop the server.
echo ===================================================================

REM Launch browser in background after 2 seconds
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

REM Launch Uvicorn with hot reload
"%VENV_DIR%\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
