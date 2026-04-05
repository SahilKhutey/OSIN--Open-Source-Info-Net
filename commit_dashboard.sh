#!/bin/bash
cd /c/Users/User/Documents/OSIN

echo "========================================"
echo "Committing Dashboard Updates to GitHub"
echo "========================================"
echo ""

# Stage all changes
echo "[1/4] Staging all changes..."
git add -A

# Check if there are changes to commit
if git diff-index --cached --quiet HEAD; then
    echo "No changes to commit."
    exit 0
fi

# Show what will be committed
echo ""
echo "[2/4] Changes to be committed:"
git diff --cached --name-only
echo ""

# Commit with message
echo "[3/4] Committing changes..."
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

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to commit changes"
    exit 1
fi

# Push to GitHub
echo ""
echo "[4/4] Pushing to GitHub..."
git push origin master

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to push to GitHub"
    echo "Try running: git push origin master"
    exit 1
fi

echo ""
echo "========================================"
echo "SUCCESS! Changes committed and pushed"
echo "========================================"
echo ""
git log --oneline -5
