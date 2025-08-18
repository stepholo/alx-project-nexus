#!/bin/bash
# render-build.sh

# Install dependencies
pip install -r requirements.txt

# Run migrations
python shopvana/manage.py migrate

# Collect static files
python shopvana/manage.py collectstatic --noinput

# Create superuser
python shopvana/manage.py shell -c "
from django.contrib.auth import get_user_model;
import os, sys;
User = get_user_model();
username=os.environ['DJANGO_SUPERUSER_USERNAME'];
email=os.environ['DJANGO_SUPERUSER_EMAIL'];
password=os.environ['DJANGO_SUPERUSER_PASSWORD'];
user, created = User.objects.get_or_create(username=username, defaults={'email': email});
user.is_active = True;
user.is_staff = True;
user.is_superuser = True;
user.set_password(password);
user.save();
msg = f'>>> Superuser {username} active={user.is_active} staff={user.is_staff} superuser={user.is_superuser}';
print(msg);
sys.stdout.flush();
"