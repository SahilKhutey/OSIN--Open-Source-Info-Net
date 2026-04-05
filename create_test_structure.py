#!/usr/bin/env python
"""Create test directory structure for OSIN"""
import os

# Base path
base_path = r'C:\Users\User\Documents\OSIN'

# List of directories to create
directories = [
    'backend/tests/unit/ingestion/social',
    'backend/tests/unit/features',
    'backend/tests/unit/agents',
    'backend/tests/unit/compliance',
    'backend/tests/integration/pipeline',
    'backend/tests/integration/kafka',
    'backend/tests/integration/ai',
    'backend/tests/streaming',
    'backend/tests/ai',
    'backend/tests/system',
    'backend/tests/ui',
    'backend/tests/load',
]

# Create directories and __init__.py files
init_content = '# Test module for OSIN'

for directory in directories:
    full_path = os.path.join(base_path, directory)
    os.makedirs(full_path, exist_ok=True)
    init_file = os.path.join(full_path, '__init__.py')
    with open(init_file, 'w') as f:
        f.write(init_content)
    print(f'Created: {directory}/__init__.py')

print(f'\nTotal directories created: {len(directories)}')
print('Test directory structure created successfully!')
