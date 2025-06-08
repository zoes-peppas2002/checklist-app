#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Create necessary directories
mkdir -p static/reports
mkdir -p temp_pdf

echo "Build completed successfully!"
