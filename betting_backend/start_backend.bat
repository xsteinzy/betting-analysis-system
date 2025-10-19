
@echo off
REM Startup script for Flask Backend API (Windows)
REM This script starts the betting analysis backend API server

echo ==========================================
echo   Betting Analysis Backend Startup
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "api\server.py" (
    echo Error: Please run this script from the betting_backend directory
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "api\.env" (
    echo Warning: No .env file found. Creating from .env.example...
    if exist "api\.env.example" (
        copy "api\.env.example" "api\.env"
        echo Created api\.env - Please configure your database credentials!
        echo Edit api\.env and add your database connection details.
        pause
        exit /b 1
    ) else (
        echo Error: .env.example not found!
        pause
        exit /b 1
    )
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created!
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade requirements
echo Installing Python dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r api\requirements.txt --quiet
if errorlevel 1 (
    echo Error: Failed to install dependencies
    call deactivate
    pause
    exit /b 1
)
echo Dependencies installed!

REM Test database connection
echo.
echo Testing database connection...
python api\connection.py
if errorlevel 1 (
    echo.
    echo Warning: Database connection test failed!
    echo Please check your database configuration in api\.env
    echo.
    pause
)

REM Start the server
echo.
echo ==========================================
echo   Starting Flask API Server
echo ==========================================
echo.
echo API will be available at: http://localhost:5000
echo Press CTRL+C to stop the server
echo.

cd api
python server.py
