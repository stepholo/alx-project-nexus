#!/usr/bin/env bash
# render-build.sh

set -o errexit  # Exit on error

# 1. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 2. Apply migrations
python shopvana/manage.py migrate

# 3. Collect static files
python shopvana/manage.py collectstatic --noinput

# 4. Create a superuser if not exists
python shopvana/manage.py createsuperuser --noinput || true
