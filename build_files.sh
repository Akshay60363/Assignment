#!/bin/bash

# Make script executable
echo "Building the project..."
python3 -m pip install -r requirements.txt

mkdir -p staticfiles
python3 manage.py collectstatic --noinput

echo "Build completed successfully." 