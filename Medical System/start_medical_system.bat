@echo off
title Medical Test System - Easy Launcher
color 0A
echo.
echo  ================================================
echo   Medical Test Data Management System v2.0
echo  ================================================
echo.
echo  Features Available:
echo  - Patient Management
echo  - Test Results Entry  
echo  - Test Type Management (NEW!)
echo  - CSV Import/Export
echo  - Custom Ranges
echo  - Report Generation
echo.
echo  ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking Python installation... OK
echo.

REM Check if main.py exists
if not exist main.py (
    echo ERROR: main.py not found in current directory
    echo Please run this batch file from the project folder
    echo.
    pause
    exit /b 1
)

echo [2/3] Checking project files... OK
echo.

REM Install/update dependencies
echo [3/3] Installing dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo WARNING: Failed to install some dependencies
    echo The application may still work with existing packages
    echo.
)

echo Dependencies check complete!
echo.
echo  ================================================
echo   Starting Medical Test System...
echo  ================================================
echo.
echo  Instructions:
echo  - Use the "Test Types" tab to add new test types
echo  - Age and gender help provide accurate ranges
echo  - CSV import supports flexible column mapping
echo  - Reports show age/gender-adjusted results
echo.
echo  Press Ctrl+C in this window to stop the application
echo  ================================================
echo.

REM Launch the application
python main.py

REM Handle application exit
echo.
echo  ================================================
echo   Medical Test System has closed
echo  ================================================
echo.
if errorlevel 1 (
    echo Application exited with an error.
    echo Check the error messages above for details.
    echo.
) else (
    echo Application closed normally.
    echo.
)

echo Press any key to exit...
pause >nul
