#!/usr/bin/env python3
"""Create React dashboard directory structure"""
import os

# Base paths
DASHBOARD_ROOT = r'c:\Users\User\Documents\OSIN\dashboard'
SRC_DIR = os.path.join(DASHBOARD_ROOT, 'src')
PUBLIC_DIR = os.path.join(DASHBOARD_ROOT, 'public')

# Directories to create
dirs = [
    DASHBOARD_ROOT,
    SRC_DIR,
    os.path.join(SRC_DIR, 'components'),
    os.path.join(SRC_DIR, 'hooks'),
    os.path.join(SRC_DIR, 'store'),
    os.path.join(SRC_DIR, 'types'),
    os.path.join(SRC_DIR, 'styles'),
    PUBLIC_DIR,
]

for dir_path in dirs:
    try:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created: {dir_path}")
    except Exception as e:
        print(f"✗ Error creating {dir_path}: {e}")

print("\n✅ Dashboard directory structure created!")
