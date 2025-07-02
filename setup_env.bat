@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM GCDM Auto Flask Application Environment Setup Script for Windows 11

echo Setting up GCDM Auto Flask Application Environment...
echo ====================================================

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python 3 is not installed or not in PATH.
    echo    Please install Python 3.8 or higher from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version') do echo ✅ Found Python: %%i

REM Check if virtual environment already exists
if exist "venv" (
    echo ⚠️  Virtual environment 'venv' already exists.
    set /p RECREATE_CHOICE="❓ Do you want to recreate it? (y/N): "
    
    if /i "!RECREATE_CHOICE!"=="y" (
        echo 🗑️  Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo ✅ Using existing virtual environment.
    )
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔧 Creating Python virtual environment...
    python -m venv venv
    
    if errorlevel 1 (
        echo ❌ Error: Failed to create virtual environment.
        echo    Please check your Python installation.
        pause
        exit /b 1
    )
    
    echo ✅ Virtual environment created successfully.
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ❌ Error: Failed to activate virtual environment
    pause
    exit /b 1
) else (
    echo ✅ Virtual environment activated: %VIRTUAL_ENV%
)

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo 📚 Installing Python dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    
    if errorlevel 1 (
        echo ❌ Error: Failed to install some dependencies.
        pause
        exit /b 1
    ) else (
        echo ✅ Dependencies installed successfully.
    )
) else (
    echo ❌ Error: requirements.txt not found.
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "app\static\uploads" mkdir app\static\uploads
if not exist "logs" mkdir logs

REM Set permissions for upload directory (Windows equivalent)
echo ✅ Upload directory created: app\static\uploads

echo.
echo 🎉 Environment setup completed successfully!
echo ==========================================
echo 📍 Virtual environment: %CD%\venv
for /f "tokens=*" %%i in ('python --version') do echo 🐍 Python version: %%i
echo 📦 Installed packages:
pip list --format=columns | findstr /n "^" | findstr "^[1-9]:" | findstr /v "^1[1-9]:"
echo    ...
echo.
echo 🚀 To start the application, run: start.bat
echo 🔧 To activate the environment manually: venv\Scripts\activate.bat
echo.
pause
