@echo off
echo ========================================
echo Starting VicobiAI Application
echo ========================================

REM Check if venv exists, if not create it
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/Update dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

REM Start FastAPI application
echo ========================================
echo Starting FastAPI server...
echo ========================================
uvicorn app.main:app --reload

REM If server stops, keep window open
pause
