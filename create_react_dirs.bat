@echo off
REM Create directory structure for React dashboard
echo Creating React Dashboard Directory Structure...

cd /d C:\Users\User\Documents\OSIN

if not exist "dashboard" mkdir dashboard
cd dashboard

if not exist "src" mkdir src
if not exist "src\components" mkdir src\components
if not exist "src\hooks" mkdir src\hooks
if not exist "src\store" mkdir src\store
if not exist "src\types" mkdir src\types
if not exist "src\styles" mkdir src\styles
if not exist "public" mkdir public

echo.
echo ✓ Directory structure created successfully!
echo.
echo Next steps:
echo 1. Navigate to: C:\Users\User\Documents\OSIN\dashboard
echo 2. Run: npm install
echo 3. Copy all component files from the provided code
echo 4. Run: npm run dev
echo.
pause
