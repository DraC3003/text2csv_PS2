@echo off
title Medical Test System - Fresh Start
color 0C
echo.
echo  ================================================
echo   Medical Test System - FRESH START
echo  ================================================
echo.
echo  ⚠️  WARNING: This will DELETE ALL DATA!
echo.
echo  This will remove:
echo  ❌ All patients
echo  ❌ All test results
echo  ❌ All test types
echo  ❌ All custom ranges
echo.
echo  A backup will be created automatically.
echo.
echo  ================================================
echo.

pause

echo.
echo 🚀 Starting fresh database reset...
python fresh_start.py

echo.
echo ================================================
if errorlevel 1 (
    echo ❌ Fresh start failed!
    echo Check the error messages above.
) else (
    echo ✅ Fresh start completed successfully!
    echo.
    echo Ready to launch clean system?
)
echo ================================================
echo.

choice /c YN /m "Launch the clean application now? (Y/N)"
if errorlevel 2 (
    echo.
    echo Use 'run.bat' to launch later.
    pause
    exit /b 0
)

echo.
echo 🚀 Launching clean Medical Test System...
python main.py

pause
