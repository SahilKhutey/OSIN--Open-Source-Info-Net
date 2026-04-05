#!/usr/bin/env python3
import os
import subprocess
import sys

# Change to the OSIN directory
os.chdir(r'C:\Users\User\Documents\OSIN')

# Create directory structure using mkdir -p equivalent
dirs_to_create = [
    r'backend\tests\unit\ingestion\social',
    r'backend\tests\unit\features',
    r'backend\tests\unit\agents',
    r'backend\tests\unit\compliance',
    r'backend\tests\integration\pipeline',
    r'backend\tests\integration\kafka',
    r'backend\tests\integration\ai',
    r'backend\tests\streaming',
    r'backend\tests\ai',
    r'backend\tests\system',
    r'backend\tests\ui',
    r'backend\tests\load'
]

for dir_path in dirs_to_create:
    os.makedirs(dir_path, exist_ok=True)
    init_file = os.path.join(dir_path, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('# Test module for OSIN\n')
    print(f'Created: {dir_path}/__init__.py')

print('\nAll test directories created successfully!')
