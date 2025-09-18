@echo off
REM VPS Startup Script with SubUser Migration
REM This script ensures the database is migrated before starting the application

echo 🚀 Starting King's Choice Management App on VPS
echo ==============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python.
    pause
    exit /b 1
)

REM Check if database file exists
if not exist "kings_choice.db" (
    echo ❌ Database file not found. Please check your setup.
    pause
    exit /b 1
)

REM Run migration script
echo 🔧 Running database migration...
python vps_subuser_migration.py

if errorlevel 1 (
    echo ❌ Migration failed. Please check the error messages above.
    pause
    exit /b 1
)

echo ✅ Migration completed successfully

REM Kill any existing Python processes
echo 🔄 Stopping any existing processes...
taskkill /f /im python.exe >nul 2>&1

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start the application
echo 🚀 Starting application...
python app.py

echo ✅ Application started successfully!
echo 🌐 Access your app at: http://your-vps-ip:5000
pause
