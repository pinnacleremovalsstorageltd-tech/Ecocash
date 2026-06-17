#!/bin/bash
# EcoCash Partner Portal - Setup Script for Linux/macOS

echo ""
echo "========================================"
echo "EcoCash Partner Portal Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source .venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[4/5] Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to run migrations"
    exit 1
fi

echo "[5/5] Creating logs directory..."
mkdir -p logs

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the development server:"
echo "  1. Activate: source .venv/bin/activate"
echo "  2. Run: python manage.py runserver"
echo ""
echo "To create a superuser:"
echo "  python manage.py createsuperuser"
echo ""
echo "Access the application at: http://localhost:8000"
echo "Admin panel at: http://localhost:8000/admin"
echo ""
