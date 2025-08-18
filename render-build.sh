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
try:
    user = User.objects.get(username=username)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    msg = f'>>> Existing superuser {username} updated and activated.'
except User.DoesNotExist:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    user.is_active = True
    user.save()
    msg = f'>>> New superuser {username} created and activated.'
print(msg)
sys.stdout.flush();
"