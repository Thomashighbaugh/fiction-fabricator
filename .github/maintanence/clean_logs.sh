#!/usr/bin/env bash

# This script cleans up the project directory by removing caches and logs.

# Find and remove all __pycache__ directories
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -r {} +

# Remove log directories
echo "Removing log directories..."
rm -rf Logs/ PremiseGenLogs/ ShortStoryLogs/ WebNovelLogs/

echo "Cleanup complete."
