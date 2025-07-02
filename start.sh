#!/bin/bash

# GCDM Auto Flask Application Startup Script

echo "Starting GCDM Auto Flask Application..."
echo "========================================"

# Check if port 8080 is in use and kill the process if needed
echo "Checking port 8080..."
PORT_PID=$(lsof -ti:8080)
if [ ! -z "$PORT_PID" ]; then
    echo ""
    echo "⚠️  ============================================== ⚠️"
    echo "⚠️  WARNING: PORT 8080 IS ALREADY IN USE!        ⚠️"
    echo "⚠️  ============================================== ⚠️"
    echo ""
    echo "🔍 Process ID: $PORT_PID"
    echo "📋 Process details:"
    ps -p $PORT_PID -o pid,ppid,cmd 2>/dev/null || echo "   Process details not available"
    echo ""
    echo "❓ Do you want to kill this process and continue? (y/N)"
    read -p "   Your choice: " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔪 Killing process $PORT_PID..."
        kill -9 $PORT_PID
        sleep 2

        # Double check if the process is really killed
        PORT_PID_CHECK=$(lsof -ti:8080)
        if [ ! -z "$PORT_PID_CHECK" ]; then
            echo "⚠️  Warning: Failed to kill process on port 8080. Trying again..."
            kill -9 $PORT_PID_CHECK
            sleep 2

            # Final check
            PORT_PID_FINAL=$(lsof -ti:8080)
            if [ ! -z "$PORT_PID_FINAL" ]; then
                echo "❌ Error: Unable to free port 8080. Please manually kill the process."
                echo "   You can try: sudo kill -9 $PORT_PID_FINAL"
                exit 1
            fi
        fi

        echo "✅ Port 8080 is now free."
    else
        echo ""
        echo "❌ Operation cancelled. Cannot start application while port 8080 is in use."
        echo "   Please stop the existing process or use a different port."
        exit 1
    fi
else
    echo "✅ Port 8080 is available."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment 'venv' not found."
    echo "Please run './setup_env.sh' first to set up the environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Error: Failed to activate virtual environment"
    echo "Please run './setup_env.sh' to recreate the environment."
    exit 1
fi

# Check if required packages are installed
echo "Checking environment health..."
python -c "import flask, sqlalchemy, yaml, pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: Some required packages are missing."
    echo "Installing/updating dependencies..."
    pip install -r requirements.txt --quiet

    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies."
        echo "Please run './setup_env.sh' to recreate the environment."
        exit 1
    fi
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found in current directory."
    exit 1
fi

# Create upload directory if it doesn't exist
mkdir -p app/static/uploads

# Display startup information
echo ""
echo "Environment Check: ✓ Passed"
echo "Python Version: $(python --version)"
echo "Flask Application: app.py"
echo "Server: http://localhost:8080 (localhost only)"
echo "Upload Directory: app/static/uploads"
echo ""
echo "Starting Flask application..."
echo "Press Ctrl+C to stop the application"
echo "========================================"

# Start the Flask application
python app.py
