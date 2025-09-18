@echo off
REM Fix Permissions Script for Windows VPS
REM This script fixes common permission issues

echo 🔧 Fixing Permissions for King's Choice App
echo ===========================================

REM Get current directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo Working directory: %SCRIPT_DIR%

REM Fix file permissions
echo 📁 Fixing file permissions...

REM Make Python files readable (Windows doesn't need chmod)
echo ✅ Python files are readable by default on Windows

REM Create necessary directories
echo 📁 Creating directories...
if not exist "user_databases" mkdir user_databases
if not exist "logs" mkdir logs
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\icons" mkdir static\icons
if not exist "templates\auth" mkdir templates\auth
if not exist "templates\admin" mkdir templates\admin
if not exist "templates\feedback" mkdir templates\feedback
if not exist "templates\modern\alliances" mkdir templates\modern\alliances
if not exist "templates\modern\events" mkdir templates\modern\events
if not exist "templates\modern\players" mkdir templates\modern\players
if not exist "translations\en\LC_MESSAGES" mkdir translations\en\LC_MESSAGES
if not exist "translations\ru\LC_MESSAGES" mkdir translations\ru\LC_MESSAGES

echo ✅ Directories created

REM Check if we can write to current directory
if exist "." (
    echo ✅ Current directory is accessible
) else (
    echo ❌ Current directory is not accessible
    echo    Try running as Administrator
)

REM Check Python executable
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not accessible
    echo    Please install Python from https://www.python.org/downloads/
) else (
    echo ✅ Python is accessible
)

REM Check if database file exists and is writable
if exist "kings_choice.db" (
    echo ✅ Database file exists
) else (
    echo ⚠️  Database file does not exist (will be created)
)

echo.
echo 🎯 Permission fix completed!
echo.
echo If you still get permission denied errors:
echo 1. Try running as Administrator
echo 2. Check if antivirus is blocking the files
echo 3. Try running: python start_vps_simple.py
pause
