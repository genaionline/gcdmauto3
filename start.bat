@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM GCDM Auto Flask Application Startup Script for Windows 11

echo Starting GCDM Auto Flask Application...
echo ========================================

REM Check if port 8080 is in use and kill the process if needed
echo Checking port 8080...

REM Find process using port 8080
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do (
    set PORT_PID=%%a
    goto :found_process
)
set PORT_PID=
:found_process

if defined PORT_PID (
    if !PORT_PID! NEQ 0 (
        echo.
        echo ⚠️  ============================================== ⚠️
        echo ⚠️  WARNING: PORT 8080 IS ALREADY IN USE!        ⚠️
        echo ⚠️  ============================================== ⚠️
        echo.
        echo 🔍 Process ID: !PORT_PID!
        echo 📋 Process details:
        tasklist /FI "PID eq !PORT_PID!" 2>nul || echo    Process details not available
        echo.
        set /p KILL_CHOICE="❓ Do you want to kill this process and continue? (y/N): "
        
        if /i "!KILL_CHOICE!"=="y" (
            echo.
            echo 🔪 Killing process !PORT_PID!...
            taskkill /PID !PORT_PID! /F >nul 2>&1
            timeout /t 2 /nobreak >nul
            
            REM Double check if the process is really killed
            for /f "tokens=5" %%b in ('netstat -aon ^| findstr :8080') do (
                set PORT_PID_CHECK=%%b
                goto :still_running
            )
            set PORT_PID_CHECK=
            :still_running
            
            if defined PORT_PID_CHECK (
                if !PORT_PID_CHECK! NEQ 0 (
                    echo ⚠️  Warning: Failed to kill process on port 8080. Trying again...
                    taskkill /PID !PORT_PID_CHECK! /F >nul 2>&1
                    timeout /t 2 /nobreak >nul
                    
                    REM Final check
                    for /f "tokens=5" %%c in ('netstat -aon ^| findstr :8080') do (
                        set PORT_PID_FINAL=%%c
                        goto :final_check
                    )
                    set PORT_PID_FINAL=
                    :final_check
                    
                    if defined PORT_PID_FINAL (
                        if !PORT_PID_FINAL! NEQ 0 (
                            echo ❌ Error: Unable to free port 8080. Please manually kill the process.
                            echo    You can try: taskkill /PID !PORT_PID_FINAL! /F
                            pause
                            exit /b 1
                        )
                    )
                )
            )
            
            echo ✅ Port 8080 is now free.
        ) else (
            echo.
            echo ❌ Operation cancelled. Cannot start application while port 8080 is in use.
            echo    Please stop the existing process or use a different port.
            pause
            exit /b 1
        )
    )
) else (
    echo ✅ Port 8080 is available.
)

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Error: Virtual environment 'venv' not found.
    echo    Please run 'setup_env.bat' first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ❌ Error: Failed to activate virtual environment
    echo    Please run 'setup_env.bat' to recreate the environment.
    pause
    exit /b 1
) else (
    echo ✅ Virtual environment activated: %VIRTUAL_ENV%
)

REM Check if required packages are installed
echo Checking environment health...
python -c "import flask, sqlalchemy, yaml, pandas, openpyxl" 2>nul
if errorlevel 1 (
    echo ⚠️  Warning: Some required packages are missing.
    echo 📦 Installing/updating dependencies...
    pip install -r requirements.txt --quiet
    
    if errorlevel 1 (
        echo ❌ Error: Failed to install dependencies.
        echo    Please run 'setup_env.bat' to recreate the environment.
        pause
        exit /b 1
    )
)

REM Check if app.py exists
if not exist "app.py" (
    echo ❌ Error: app.py not found in current directory.
    pause
    exit /b 1
)

REM Create upload directory if it doesn't exist
if not exist "app\static\uploads" mkdir app\static\uploads

REM Display startup information
echo.
echo ✅ Environment Check: Passed
for /f "tokens=*" %%i in ('python --version') do echo 🐍 Python Version: %%i
echo 🚀 Flask Application: app.py
echo 🌐 Server: http://localhost:8080 (localhost only)
echo 📁 Upload Directory: app\static\uploads
echo.
echo 🎯 Starting Flask application...
echo 🛑 Press Ctrl+C to stop the application
echo ========================================
echo.

REM Start the Flask application
python app.py
