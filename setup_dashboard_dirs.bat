@echo off
REM Create dashboard directory structure
cd /d C:\Users\User\Documents\OSIN

if not exist "dashboard" mkdir dashboard
cd dashboard

if not exist "src" mkdir src
if not exist "src\components" mkdir src\components
if not exist "src\hooks" mkdir src\hooks
if not exist "src\store" mkdir src\store
if not exist "src\types" mkdir src\types
if not exist "src\services" mkdir src\services
if not exist "public" mkdir public

echo ✓ Dashboard directory structure created successfully!
python ..\setup_dashboard.py
