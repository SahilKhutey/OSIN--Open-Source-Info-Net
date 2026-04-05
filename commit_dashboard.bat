@echo off
cd /d c:\Users\User\Documents\OSIN

echo.
echo ========================================
echo Committing Dashboard Updates to GitHub
echo ========================================
echo.

REM Stage all changes
echo [1/4] Staging all changes...
git add -A
if %errorlevel% neq 0 (
    echo ERROR: Failed to stage changes
    exit /b 1
)

REM Check if there are changes to commit
git diff-index --cached --quiet HEAD
if %errorlevel% eq 0 (
    echo No changes to commit.
    exit /b 0
)

REM Show what will be committed
echo.
echo [2/4] Changes to be committed:
git diff --cached --name-only
echo.

REM Commit with message
echo [3/4] Committing changes...
git commit -m "Rebuild dashboard with dynamic terminal-style interface for real-time intelligence signals

- Replaced glass-morphism design with authentic terminal UI
- Added live signal feed with real-time ingestion visualization
- Implemented threat assessment panel with live level indicators
- Added trending keywords tracker across all platforms
- Implemented source distribution metrics (Twitter, Reddit, YouTube, News, Instagram, LinkedIn)
- Added system status monitoring (API, Data Stream, Processing)
- Created interactive signal detail modal with credibility breakdown
- Live uptime and ingestion rate tracking
- Terminal-style green monospace font with scanline effects
- Real-time data updates every 3-5 seconds matching OSIN ingestion architecture

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

if %errorlevel% neq 0 (
    echo ERROR: Failed to commit changes
    exit /b 1
)

REM Push to GitHub
echo.
echo [4/4] Pushing to GitHub...
git push origin master
if %errorlevel% neq 0 (
    echo ERROR: Failed to push to GitHub
    echo Try running: git push origin master
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Changes committed and pushed
echo ========================================
echo.
git log --oneline -5

pause
