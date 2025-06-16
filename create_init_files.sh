#!/bin/bash
# Create missing __init__.py files

echo "Creating __init__.py files..."

# Create empty __init__.py files
touch models/__init__.py
touch experiments/__init__.py
touch prompts/__init__.py
touch data/__init__.py

# Verify they were created
echo "Verification:"
ls -la models/__init__.py experiments/__init__.py prompts/__init__.py data/__init__.py

echo "✅ __init__.py files created successfully!"