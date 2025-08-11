# Simple Medical System PowerShell Script
Write-Host "Medical Test Management System" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

Write-Host ""
Write-Host "System Status Check:" -ForegroundColor Yellow

if (Test-Path "main.py") {
    Write-Host "✓ Main application found" -ForegroundColor Green
} else {
    Write-Host "✗ Main application missing" -ForegroundColor Red
}

if (Test-Path "medical_test_data.db") {
    Write-Host "✓ Database found" -ForegroundColor Green  
} else {
    Write-Host "✗ Database missing" -ForegroundColor Red
}

Write-Host ""
Write-Host "Method field integration test:" -ForegroundColor Yellow
python test_method_field.py

Write-Host ""
Write-Host "To run the medical system:" -ForegroundColor Cyan
Write-Host "python main.py" -ForegroundColor White

Write-Host ""
