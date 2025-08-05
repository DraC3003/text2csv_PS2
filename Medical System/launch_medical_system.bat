@echo off
title Medical Test System - Launcher
color 0A
echo.
echo  ================================================
echo   Medical Test System - Starting Up
echo  ================================================
echo.
echo  🔍 Checking system status...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ Python not found! Please install Python.
    pause
    exit /b 1
)

echo  ✅ Python is available
echo.
echo  🗃️ Checking database...

if exist medical_test_data.db (
    echo  ✅ Database found
) else (
    echo  ⚠️ Database not found - will be created automatically
)

echo.
echo  🚀 Launching Medical Test System...
echo  ⏳ Please wait for the GUI window to appear...
echo.
echo  💡 Tips:
echo     - The window might open behind other windows
echo     - Look for the application in your taskbar
echo     - If you see a matplotlib warning, you can ignore it
echo.

REM Launch the application
python main.py

echo.
if errorlevel 1 (
    echo  ❌ Application failed to start
    echo.
    echo  🔧 Troubleshooting:
    echo     1. Run debug_launcher.py for detailed diagnostics
    echo     2. Run fresh_start.py to reset the database
    echo     3. Check if all files are present
    echo.
) else (
    echo  ✅ Application closed normally
)

pause
