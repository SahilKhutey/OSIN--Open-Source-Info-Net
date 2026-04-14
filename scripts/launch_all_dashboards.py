"""
OSIN Complete Dashboard Launcher (Python - Cross-platform)
Starts backend and frontend with a single command
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

class DashboardLauncher:
    def __init__(self):
        self.base_path = Path(r"C:\Users\User\Documents\OSIN")
        self.frontend_path = self.base_path / "frontend"
        self.backend_path = self.base_path / "backend"
        self.dashboard_path = self.base_path / "dashboard"
        
    def print_header(self):
        print("\n")
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║   OSIN INTELLIGENCE DASHBOARD - COMPLETE LAUNCHER             ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print("\n")
        
    def check_directories(self):
        print("[1/4] Checking directories...")
        
        if not self.frontend_path.exists():
            print("✗ Frontend directory not found!")
            sys.exit(1)
        if not self.backend_path.exists():
            print("✗ Backend directory not found!")
            sys.exit(1)
        
        print("✓ Directories verified")
        print()
        
    def start_backend(self):
        print("[2/4] Starting Backend Server...")
        print()
        
        # Change to backend directory
        os.chdir(str(self.backend_path))
        
        # Start backend
        try:
            subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", 
                 "--reload", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("⏳ Waiting for backend to initialize... (5 seconds)")
            time.sleep(5)
            print("✓ Backend started on http://localhost:8000")
            print()
        except Exception as e:
            print(f"✗ Failed to start backend: {e}")
            sys.exit(1)
            
        # Return to base path
        os.chdir(str(self.base_path))
        
    def launch_dashboards(self):
        print("[3/4] Opening Dashboards...")
        print()
        
        # Terminal Dashboard
        print("Launching Terminal Dashboard...")
        terminal_url = f"file:///{str(self.frontend_path / 'index.html').replace(chr(92), '/')}"
        webbrowser.open(terminal_url)
        time.sleep(2)
        
        # API Docs
        print("Launching API Documentation...")
        webbrowser.open("http://localhost:8000/docs")
        time.sleep(2)
        
        # React Dashboard
        if (self.dashboard_path / "package.json").exists():
            response = input("Start React 3D Dashboard? (Y/N): ").strip().upper()
            if response == "Y":
                print("Starting React dashboard...")
                os.chdir(str(self.dashboard_path))
                subprocess.Popen(
                    [sys.executable, "-m", "npm", "run", "dev"] 
                    if sys.platform == "win32"
                    else ["npm", "run", "dev"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print("⏳ Waiting for React to initialize... (10 seconds)")
                time.sleep(10)
                print("Launching React dashboard...")
                webbrowser.open("http://localhost:5173")
                os.chdir(str(self.base_path))
                
    def print_summary(self):
        print()
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║                    ✓ DASHBOARDS LAUNCHED                      ║")
        print("╠════════════════════════════════════════════════════════════════╣")
        print("║                                                                ║")
        print("║  AVAILABLE:                                                    ║")
        terminal_url = f"file:///{str(self.frontend_path / 'index.html').replace(chr(92), '/')}"
        print(f"║  • Terminal Dashboard: {terminal_url}          ║")
        print("║                                                                ║")
        print("║  • API Documentation: http://localhost:8000/docs              ║")
        print("║                                                                ║")
        print("║  • Health Check: http://localhost:8000/health                 ║")
        print("║                                                                ║")
        
        if (self.dashboard_path / "src" / "App.tsx").exists():
            print("║  • React 3D Dashboard: http://localhost:5173                 ║")
            print("║                                                                ║")
        
        print("║  Backend: http://0.0.0.0:8000                                  ║")
        print("║  WebSocket: ws://localhost:8000/ws/intelligence                ║")
        print("║                                                                ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()
        
    def run(self):
        try:
            self.print_header()
            self.check_directories()
            self.start_backend()
            self.launch_dashboards()
            self.print_summary()
            
            print("Dashboards running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nShutting down dashboards...")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    launcher = DashboardLauncher()
    launcher.run()
