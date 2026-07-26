import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oncoscience.settings')
django.setup()

from django.contrib.auth.models import User
import secrets
import string

# Deactivate old admins
for username in ['admin', 'admin_master']:
    try:
        u = User.objects.get(username=username)
        u.is_active = False
        u.is_superuser = False
        u.is_staff = False
        u.save()
        print(f"Deactivated {username}")
    except User.DoesNotExist:
        print(f"{username} does not exist")

# Create new superuser
new_username = 'admin_cancercenter'
try:
    u = User.objects.get(username=new_username)
    print(f"Superuser {new_username} already exists.")
except User.DoesNotExist:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(16))
    u = User.objects.create_superuser(username=new_username, email='admin@cancercenter.uz', password=password)
    print(f"Created new superuser: {new_username}")
    print(f"PASSWORD: {password}")
