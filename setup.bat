@echo off
REM Faculty Management System - Quick Setup Script for Windows

echo ================================================
echo Faculty Management System - Setup
echo ================================================
echo.

REM 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo Python found.
echo.

REM 2. Setup Virtual Environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment (.venv) already exists.
)

REM 3. Activate Virtual Environment
echo Activating virtual environment...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)
echo Virtual environment activated.
echo.

REM 4. Install Dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)
echo Dependencies installed.
echo.

REM 5. Initialize Database
echo Initializing database...
set FLASK_APP=app
python -m flask init-db
if %errorlevel% neq 0 (
    echo Failed to initialize database.
    pause
    exit /b 1
)
echo Database initialized.
echo.

REM 6. Seed Database
echo Seeding database...
python -m flask seed-db
echo.

REM 7. Create Admin User (Optional)
echo ================================================
echo               ADMIN USER SETUP
echo ================================================
set /p create_admin="Do you want to create an Admin user now? (Y/N): "
if /i "%create_admin%"=="Y" (
    echo.
    echo Running Admin Creation Wizard...
    python -m flask create-admin
) else (
    echo Skipping admin creation. You can run 'flask create-admin' later.
)
echo.

echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo To start the application:
echo 1. .venv\Scripts\activate
echo 2. python app.py
echo.
pause
