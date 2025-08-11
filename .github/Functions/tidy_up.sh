#!/usr/bin/env bash

# Remove Pycache Files
find . -type d -name "__pycache__" -exec rm -r {} +

# Remove Logs directory
rm -rf Logs/
