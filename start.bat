@echo off
setlocal

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ============================================
echo   Selenium Eligibility Automation - Startup
echo ============================================
echo.

:: Check Python is installed and in PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    echo         Please install Python 3.8+ from https://www.python.org and try again.
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version
echo.

:: Check Chrome is installed (required for Selenium)
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Google Chrome not detected in registry.
    echo           Chrome is required to run Selenium tests.
    echo           Download from: https://www.google.com/chrome/
    echo.
    echo           If Chrome is installed but not detected, you can continue anyway.
    pause
)

:: Check eligibility_form.html is present in test_pages folder
if not exist "%PROJECT_DIR%test_pages\eligibility_form.html" (
    echo [ERROR] test_pages\eligibility_form.html not found.
    echo         Please ensure all project files are present and try again.
    pause
    exit /b 1
)

echo [INFO] eligibility_form.html found in test_pages\.
echo.

:: Check if venv exists
if exist "%PROJECT_DIR%venv\Scripts\activate.bat" (
    echo [INFO] Found existing virtual environment.
    goto :activate
)

:: venv not found — create it and install dependencies
echo [INFO] No virtual environment found. Creating one...
python -m venv venv

if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    echo         Make sure Python is installed correctly and try again.
    pause
    exit /b 1
)

echo [INFO] Virtual environment created. Installing dependencies...
echo [INFO] Note: webdriver-manager will auto-download ChromeDriver on first run.
echo.
call "%PROJECT_DIR%venv\Scripts\activate.bat"
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    echo         Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [INFO] Dependencies installed successfully.
goto :run

:activate
echo [INFO] Activating virtual environment...
call "%PROJECT_DIR%venv\Scripts\activate.bat"
echo [INFO] Virtual environment activated.
echo.

:run
echo [INFO] Generating test data...
python generate_test_data.py

if errorlevel 1 (
    echo [ERROR] Failed to generate test data.
    pause
    exit /b 1
)

echo.
echo [INFO] Running Selenium test suite...
echo [INFO] Chrome will open and close automatically during testing.
echo [INFO] Do not interact with the browser while tests are running.
echo.
pytest test_eligibility_form.py -v

echo.
echo [INFO] Test run complete. Check above for results.
echo [INFO] Test results are also saved to test_results.csv in the project folder.
pause
