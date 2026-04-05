#!/usr/bin/env python3
"""
Git commit and push script for OSIN dashboard changes
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and return success/failure"""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, cwd=r'c:\Users\User\Documents\OSIN', 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"ERROR: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("=" * 50)
    print("Committing Dashboard Updates to GitHub")
    print("=" * 50)

    # Stage changes
    if not run_command("git add -A", "Staging all changes"):
        return False

    # Check if there are changes
    check = subprocess.run("git diff-index --cached --quiet HEAD", 
                          shell=True, cwd=r'c:\Users\User\Documents\OSIN')
    if check.returncode == 0:
        print("\n✓ No changes to commit")
        return True

    # Show changes
    print("\n[*] Changes to be committed:")
    run_command("git diff --cached --name-only", "Listing changes")

    # Commit
    commit_msg = """Rebuild dashboard with dynamic terminal-style interface for real-time intelligence signals

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

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"""

    cmd = f'git commit -m "{commit_msg}"'
    if not run_command(cmd, "Committing changes"):
        return False

    # Push
    if not run_command("git push origin master", "Pushing to GitHub"):
        print("\nNote: If push fails, check your GitHub credentials or branch name")
        return False

    # Show recent commits
    print("\n" + "=" * 50)
    print("SUCCESS! Changes committed and pushed")
    print("=" * 50)
    run_command("git log --oneline -5", "Recent commits")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
