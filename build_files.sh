#!/bin/bash

# Make script executable
echo "Building the project..."
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

echo "Build completed successfully." 