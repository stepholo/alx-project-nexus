#!/usr/bin/env bash
echo "📂 Current directory:"
pwd

echo "📂 Listing files in current directory:"
ls -la

echo "📂 Recursively listing structure:"
ls -R

set -o errexit  # Exit on error

# 1. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 2. Apply migrations
python manage.py migrate

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Create a superuser if not exists
python manage.py createsuperuser --noinput || true
