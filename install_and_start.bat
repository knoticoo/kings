@echo off
REM King's Choice Management App - Complete Windows Installation and Startup Script
REM This script handles everything: dependencies, environment, migration, and startup

echo 🚀 King's Choice Management App - Windows Installation Script
echo ============================================================

REM Get the directory where the script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [INFO] Working directory: %SCRIPT_DIR%

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    echo [INFO] Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% found

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed. Please install pip.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo [INFO] Installing Python dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [SUCCESS] Dependencies installed from requirements.txt
) else (
    echo [WARNING] requirements.txt not found, installing basic dependencies...
    pip install flask flask-login flask-sqlalchemy flask-babel python-dotenv werkzeug
    echo [SUCCESS] Basic dependencies installed
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
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
echo [SUCCESS] Directories created

REM Set up environment variables
echo [INFO] Setting up environment variables...
if not exist ".env" (
    echo # Flask Configuration > .env
    echo FLASK_APP=app.py >> .env
    echo FLASK_ENV=production >> .env
    echo SECRET_KEY=default-secret-key-change-in-production >> .env
    echo. >> .env
    echo # Database Configuration >> .env
    echo DATABASE_URL=sqlite:///kings_choice.db >> .env
    echo. >> .env
    echo # Language Configuration >> .env
    echo DEFAULT_LANGUAGE=en >> .env
    echo SUPPORTED_LANGUAGES=en,ru >> .env
    echo. >> .env
    echo # Server Configuration >> .env
    echo HOST=0.0.0.0 >> .env
    echo PORT=5000 >> .env
    echo DEBUG=False >> .env
    echo [SUCCESS] Environment file created
) else (
    echo [INFO] Environment file already exists
)

REM Database migration and setup
echo [INFO] Setting up database...
python -c "
import os
import sys
sys.path.insert(0, '.')

from flask import Flask
from database import db, init_app, create_all_tables
from models import User, SubUser

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kings_choice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'default-secret-key-change-in-production'

# Initialize database
init_app(app)

with app.app_context():
    try:
        # Create all tables
        create_all_tables(app)
        print('✅ Database tables created successfully')
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='knotico').first()
        if not admin_user:
            print('⚠️  No admin user found. You may need to create one.')
        else:
            print('✅ Admin user found')
            
    except Exception as e:
        print(f'❌ Database setup failed: {e}')
        sys.exit(1)
"

if errorlevel 1 (
    echo [ERROR] Database setup failed
    pause
    exit /b 1
)

echo [SUCCESS] Database setup completed

REM Create startup script
echo [INFO] Creating startup script...
echo @echo off > start_app.bat
echo cd /d "%%~dp0" >> start_app.bat
echo call venv\Scripts\activate.bat >> start_app.bat
echo set FLASK_APP=app.py >> start_app.bat
echo set FLASK_ENV=production >> start_app.bat
echo set SECRET_KEY=default-secret-key-change-in-production >> start_app.bat
echo set DATABASE_URL=sqlite:///kings_choice.db >> start_app.bat
echo set HOST=0.0.0.0 >> start_app.bat
echo set PORT=5000 >> start_app.bat
echo set DEBUG=False >> start_app.bat
echo python app.py >> start_app.bat
echo pause >> start_app.bat

echo [SUCCESS] Startup script created

REM Create stop script
echo [INFO] Creating stop script...
echo @echo off > stop_app.bat
echo taskkill /f /im python.exe ^>nul 2^>^&1 >> stop_app.bat
echo echo Application stopped >> stop_app.bat
echo pause >> stop_app.bat

echo [SUCCESS] Stop script created

REM Create status script
echo [INFO] Creating status script...
echo @echo off > status_app.bat
echo echo === King's Choice App Status === >> status_app.bat
echo echo. >> status_app.bat
echo echo Process Status: >> status_app.bat
echo tasklist ^| findstr python.exe ^|^| echo No Python processes running >> status_app.bat
echo echo. >> status_app.bat
echo echo Port Status: >> status_app.bat
echo netstat -an ^| findstr :5000 ^|^| echo Port 5000 not in use >> status_app.bat
echo pause >> status_app.bat

echo [SUCCESS] Status script created

REM Start the application
echo [INFO] Starting application...
start "King's Choice App" cmd /k "call venv\Scripts\activate.bat && set FLASK_APP=app.py && set FLASK_ENV=production && set SECRET_KEY=default-secret-key-change-in-production && set DATABASE_URL=sqlite:///kings_choice.db && set HOST=0.0.0.0 && set PORT=5000 && set DEBUG=False && python app.py"

REM Wait a moment for startup
timeout /t 5 /nobreak >nul

REM Test the application
echo [INFO] Testing application...
timeout /t 3 /nobreak >nul
curl -s -o nul -w "%%{http_code}" http://localhost:5000 | findstr "200" >nul
if errorlevel 1 (
    echo [WARNING] Application may not be responding correctly. Check the application window for details.
) else (
    echo [SUCCESS] Application is responding correctly
)

REM Display final information
echo.
echo 🎉 Installation and startup completed successfully!
echo ==================================================
echo.
echo 📋 Management Scripts:
echo   Start:   start_app.bat
echo   Stop:    stop_app.bat
echo   Status:  status_app.bat
echo.
echo 🌐 Application Access:
echo   Local:   http://localhost:5000
echo   Network: http://%COMPUTERNAME%:5000
echo.
echo 📁 Important Files:
echo   App Directory: %SCRIPT_DIR%
echo   Database:      %SCRIPT_DIR%kings_choice.db
echo   Config:        %SCRIPT_DIR%.env
echo.
echo [SUCCESS] Setup complete! Your King's Choice Management App is now running.
echo [INFO] The application window should be open. If not, run start_app.bat
pause
