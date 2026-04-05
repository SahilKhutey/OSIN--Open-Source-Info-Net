@echo off
cd /d C:\Users\User\Documents\OSIN

REM Create unit test directories
mkdir backend\tests\unit\ingestion\social
mkdir backend\tests\unit\features
mkdir backend\tests\unit\agents
mkdir backend\tests\unit\compliance

REM Create integration test directories
mkdir backend\tests\integration\pipeline
mkdir backend\tests\integration\kafka
mkdir backend\tests\integration\ai

REM Create other test directories
mkdir backend\tests\streaming
mkdir backend\tests\ai
mkdir backend\tests\system
mkdir backend\tests\ui
mkdir backend\tests\load

REM Create __init__.py files
(echo # Test module for OSIN) > backend\tests\unit\ingestion\social\__init__.py
(echo # Test module for OSIN) > backend\tests\unit\features\__init__.py
(echo # Test module for OSIN) > backend\tests\unit\agents\__init__.py
(echo # Test module for OSIN) > backend\tests\unit\compliance\__init__.py
(echo # Test module for OSIN) > backend\tests\integration\pipeline\__init__.py
(echo # Test module for OSIN) > backend\tests\integration\kafka\__init__.py
(echo # Test module for OSIN) > backend\tests\integration\ai\__init__.py
(echo # Test module for OSIN) > backend\tests\streaming\__init__.py
(echo # Test module for OSIN) > backend\tests\ai\__init__.py
(echo # Test module for OSIN) > backend\tests\system\__init__.py
(echo # Test module for OSIN) > backend\tests\ui\__init__.py
(echo # Test module for OSIN) > backend\tests\load\__init__.py

echo Test directory structure created successfully!
