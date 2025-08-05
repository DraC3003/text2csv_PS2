@echo off
title Medical Test System
echo.
echo  🏥 Medical Test Data Management System
echo  =====================================
echo.
echo  Starting application...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ❌ Error occurred. Check messages above.
    echo.
    pause
) else (
    echo.
    echo ✅ Application closed normally.
)
