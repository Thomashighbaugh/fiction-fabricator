#!/usr/bin/env bash

# Create virtual environment
if ! python -m venv .venv; then
  echo "Error: Failed to create virtual environment."
  exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
if ! pip install -r requirements.txt; then
  echo "Error: Failed to install dependencies. Make sure 'requirements.txt' exists."
  exit 1
fi

echo "Virtual environment created and dependencies installed successfully."
echo "Activate the virtual environment in your current shell using: source .venv/bin/activate"
echo "Then run the application using the './run' script."

    