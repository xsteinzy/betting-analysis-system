
#!/bin/bash

# Startup script for Flask Backend API
# This script starts the betting analysis backend API server

echo "=========================================="
echo "  Betting Analysis Backend Startup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "api/server.py" ]; then
    echo "Error: Please run this script from the betting_backend directory"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if .env file exists
if [ ! -f "api/.env" ]; then
    echo "Warning: No .env file found. Creating from .env.example..."
    if [ -f "api/.env.example" ]; then
        cp api/.env.example api/.env
        echo "Created api/.env - Please configure your database credentials!"
        echo "Edit api/.env and add your database connection details."
        exit 1
    else
        echo "Error: .env.example not found!"
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created!"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r api/requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    deactivate
    exit 1
fi
echo "Dependencies installed!"

# Test database connection
echo ""
echo "Testing database connection..."
python3 api/connection.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Warning: Database connection test failed!"
    echo "Please check your database configuration in api/.env"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        deactivate
        exit 1
    fi
fi

# Start the server
echo ""
echo "=========================================="
echo "  Starting Flask API Server"
echo "=========================================="
echo ""
echo "API will be available at: http://localhost:5000"
echo "Press CTRL+C to stop the server"
echo ""

cd api
python3 server.py
