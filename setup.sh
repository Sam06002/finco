#!/bin/bash
set -e  # Exit on error

echo "=== Starting Setup ==="
echo "Current directory: $(pwd)"

# Update pip
echo "Updating pip..."
python3.11 -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
python3.11 -m pip install -r requirements.txt

# Create necessary directories
echo "Creating data directory..."
mkdir -p data

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Initialize database
echo "Initializing database..."
python3.11 -c "from db import init_db; init_db()"

# Run database migrations if needed
echo "Running database migrations..."
alembic upgrade head

echo "=== Setup Completed Successfully ==="
exit 0
