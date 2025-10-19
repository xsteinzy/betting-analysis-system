
@echo off
REM Startup script for Next.js Dashboard (Windows)
REM This script starts the betting analysis dashboard

echo ==========================================
echo   Betting Dashboard Startup
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo Error: Please run this script from the betting_dashboard directory
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

REM Check if .env.local file exists
if not exist ".env.local" (
    echo Warning: No .env.local file found. Creating from .env.local.example...
    if exist ".env.local.example" (
        copy ".env.local.example" ".env.local"
        echo Created .env.local with default settings
    ) else (
        echo Error: .env.local.example not found!
        pause
        exit /b 1
    )
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing Node.js dependencies (this may take a few minutes)...
    call npm install
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed!
) else (
    echo Dependencies already installed
)

REM Check if backend is running
echo.
echo Checking if backend API is running...
REM Simple check - this might not work on all Windows versions
curl -s http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    echo Warning: Backend API might not be running at http://localhost:5000
    echo Please start the backend first using start_backend.bat
    echo.
    pause
)

REM Start the dashboard
echo.
echo ==========================================
echo   Starting Next.js Dashboard
echo ==========================================
echo.
echo Dashboard will be available at: http://localhost:3000
echo Press CTRL+C to stop the server
echo.

npm run dev
