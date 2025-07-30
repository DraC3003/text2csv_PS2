@echo off
echo Installing required dependencies...
pip install -r requirements.txt

echo.
echo Starting SD Card Text-to-CSV Converter...
echo.
python text2csv.py

pause
