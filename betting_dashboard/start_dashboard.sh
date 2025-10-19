
#!/bin/bash

# Startup script for Next.js Dashboard
# This script starts the betting analysis dashboard

echo "=========================================="
echo "  Betting Dashboard Startup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "Error: Please run this script from the betting_dashboard directory"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check if .env.local file exists
if [ ! -f ".env.local" ]; then
    echo "Warning: No .env.local file found. Creating from .env.local.example..."
    if [ -f ".env.local.example" ]; then
        cp .env.local.example .env.local
        echo "Created .env.local with default settings"
    else
        echo "Error: .env.local.example not found!"
        exit 1
    fi
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies (this may take a few minutes)..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed!"
else
    echo "Dependencies already installed"
fi

# Check if backend is running
echo ""
echo "Checking if backend API is running..."
backend_url=$(grep NEXT_PUBLIC_API_URL .env.local | cut -d '=' -f2)
if [ -z "$backend_url" ]; then
    backend_url="http://localhost:5000"
fi

if curl -s "${backend_url}/api/health" > /dev/null 2>&1; then
    echo "✓ Backend API is running!"
else
    echo "⚠ Warning: Backend API is not responding at ${backend_url}"
    echo "Please start the backend first using start_backend.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the dashboard
echo ""
echo "=========================================="
echo "  Starting Next.js Dashboard"
echo "=========================================="
echo ""
echo "Dashboard will be available at: http://localhost:3000"
echo "Press CTRL+C to stop the server"
echo ""

npm run dev
