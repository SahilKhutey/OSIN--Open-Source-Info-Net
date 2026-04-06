@echo off
REM Create React Dashboard Directory Structure

set DASHBOARD=c:\Users\User\Documents\OSIN\dashboard
set SRC=%DASHBOARD%\src

echo Creating directories...

mkdir "%DASHBOARD%" 2>nul
mkdir "%SRC%" 2>nul
mkdir "%SRC%\components" 2>nul
mkdir "%SRC%\hooks" 2>nul
mkdir "%SRC%\store" 2>nul
mkdir "%SRC%\types" 2>nul
mkdir "%SRC%\styles" 2>nul
mkdir "%DASHBOARD%\public" 2>nul

echo.
echo ✓ Dashboard directories created:
echo   - %DASHBOARD%\src\components
echo   - %DASHBOARD%\src\hooks
echo   - %DASHBOARD%\src\store
echo   - %DASHBOARD%\src\types
echo   - %DASHBOARD%\src\styles
echo   - %DASHBOARD%\public
echo.
echo Ready for React files!
pause
