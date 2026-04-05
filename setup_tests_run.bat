@echo off
REM Change to OSIN directory
cd /d "C:\Users\User\Documents\OSIN"

REM Run Python script
echo Creating test directory structure...
python create_test_structure.py

if %ERRORLEVEL% == 0 (
    echo.
    echo Success! Test directories created.
    pause
) else (
    echo.
    echo Error occurred while creating directories
    pause
)
