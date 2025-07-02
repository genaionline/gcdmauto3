#!/bin/bash

# GCDM Auto Flask Application Environment Setup Script

echo "Setting up GCDM Auto Flask Application Environment..."
echo "===================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version)
echo "Found Python: $PYTHON_VERSION"

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "Virtual environment 'venv' already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    
    echo "Virtual environment created successfully."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "Dependencies installed successfully."
    else
        echo "Error: Failed to install some dependencies."
        exit 1
    fi
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p app/static/uploads
mkdir -p logs

# Set permissions for upload directory
chmod 755 app/static/uploads

echo ""
echo "Environment setup completed successfully!"
echo "========================================"
echo "Virtual environment: $(pwd)/venv"
echo "Python version: $(python --version)"
echo "Installed packages:"
pip list --format=columns | head -10
echo "..."
echo ""
echo "To start the application, run: ./start.sh"
echo "To activate the environment manually: source venv/bin/activate"
