#!/usr/bin/env python3
"""
OSIN React 3D Dashboard - Automated Setup Script
Creates all directories and files for the React dashboard
"""

import os
import sys
from pathlib import Path

# Define the base path
BASE_PATH = Path("C:\\Users\\User\\Documents\\OSIN\\dashboard")
SRC_PATH = BASE_PATH / "src"

# Define all files with their content
FILES = {
    "package.json": '''{
  "name": "osin-dashboard",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.1",
    "three": "^0.150.1",
    "react-globe.gl": "^2.28.0",
    "zustand": "^4.3.2"
  },
  "devDependencies": {
    "@types/node": "^18.15.0",
    "@types/three": "^0.149.0",
    "@types/react": "^18.0.28",
    "@types/react-dom": "^18.0.11",
    "typescript": "^4.9.5",
    "vite": "^4.1.0",
    "@vitejs/plugin-react": "^3.1.0"
  }
}''',
    
    "tsconfig.json": '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "strict": true,
    "esModuleInterop": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}''',

    "tsconfig.node.json": '''{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}''',

    "vite.config.ts": '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})''',

    "public/index.html": '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OSIN - Open Source Intelligence Network</title>
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      body {
        background-color: #0a0a0a;
        color: #00ff00;
        font-family: 'Courier New', monospace;
        overflow-x: hidden;
      }
      #root {
        min-height: 100vh;
      }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>''',

    "src/main.tsx": '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)''',
}

def create_directories():
    """Create all necessary directories"""
    directories = [
        BASE_PATH,
        SRC_PATH,
        SRC_PATH / "components",
        SRC_PATH / "hooks",
        SRC_PATH / "store",
        SRC_PATH / "types",
        SRC_PATH / "styles",
        BASE_PATH / "public"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")

def create_files():
    """Create all necessary files"""
    for file_path, content in FILES.items():
        full_path = BASE_PATH / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Created: {file_path}")

def main():
    print("=" * 60)
    print("OSIN React 3D Dashboard - Setup Script")
    print("=" * 60)
    print()
    
    try:
        print("Creating directories...")
        create_directories()
        print()
        
        print("Creating configuration files...")
        create_files()
        print()
        
        print("=" * 60)
        print("✓ Setup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. cd C:\\Users\\User\\Documents\\OSIN\\dashboard")
        print("2. npm install")
        print("3. Copy component files (see REACT_SETUP_GUIDE.md)")
        print("4. npm run dev")
        print()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
