#!/usr/bin/env bash
set -o errexit  # Exit on error

# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply migrations
python manage.py migrate

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Create a superuser if not exists
python manage.py createsuperuser --noinput || true
