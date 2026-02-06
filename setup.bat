@echo off
REM Faculty Management System - Quick Setup Script for Windows

echo ================================================
echo Faculty Management System - Quick Setup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python found
python --version
echo.

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not installed
    echo Please ensure pip is included with your Python installation
    pause
    exit /b 1
)

echo pip found
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully
echo.

REM Initialize database
echo Initializing database...
flask --app app init-db

if %errorlevel% neq 0 (
    echo Failed to initialize database
    pause
    exit /b 1
)

echo Database initialized successfully
echo.

REM Seed database
echo Seeding database with sample data...
flask --app app seed-db

if %errorlevel% neq 0 (
    echo Warning: Failed to seed database (this is optional)
)

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo To start the application, run:
echo   python app.py
echo.
echo Or using Flask CLI:
echo   flask --app app run --debug
echo.
echo Then open your browser to: http://127.0.0.1:5000
echo.
echo ================================================
pause
