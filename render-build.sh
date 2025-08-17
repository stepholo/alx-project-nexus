#!/usr/bin/env bash
# render-build.sh

set -o errexit  # Exit on error

# 1. Upgrade pip & install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 2. Collect static files (build-time)
python shopvana/manage.py collectstatic --noinput