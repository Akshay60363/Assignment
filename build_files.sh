#!/bin/bash

# Make script executable
echo "Building the project..."
python3 -m pip install -r requirements.txt

echo "Collecting static files..."
rm -rf staticfiles
mkdir -p staticfiles
python3 manage.py collectstatic --noinput --clear

echo "Build completed successfully." 