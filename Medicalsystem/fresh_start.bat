@echo off
cd /d "%~dp0"
echo.
echo ====================================================
echo   MEDICAL SYSTEM - COMPLETE FRESH START
echo ====================================================
echo.
echo This will delete ALL data and start fresh!
echo.
pause
echo.
echo Running fresh start...
echo.

REM Try different Python commands
if exist "ultimate_clean_start.py" (
    echo Found Python script, attempting to run...
    python ultimate_clean_start.py
    if errorlevel 1 (
        echo Python command failed, trying py...
        py ultimate_clean_start.py
        if errorlevel 1 (
            echo Both python and py failed, trying python3...
            python3 ultimate_clean_start.py
        )
    )
) else (
    echo ERROR: ultimate_clean_start.py not found!
)

echo.
echo Fresh start completed!
echo Press any key to exit...
pause >nul
