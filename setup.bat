@echo off
REM EcoCash Partner Portal - Setup Script

echo.
echo ========================================
echo EcoCash Partner Portal Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo [5/5] Creating logs directory...
if not exist logs mkdir logs

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the development server:
echo   1. Activate: .venv\Scripts\activate.bat
echo   2. Run: python manage.py runserver
echo.
echo To create a superuser:
echo   python manage.py createsuperuser
echo.
echo Access the application at: http://localhost:8000
echo Admin panel at: http://localhost:8000/admin
echo.
pause
