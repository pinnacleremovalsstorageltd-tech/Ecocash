import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db.sqlite3'

if DB_PATH.exists():
    DB_PATH.unlink()
    print('Deleted existing database:', DB_PATH)
else:
    print('No existing database to delete.')

os.chdir(BASE_DIR)

# Apply migrations
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecocash_clone.settings')
django.setup()
from django.core.management import call_command
call_command('migrate', verbosity=1)

# Create or update superuser
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin480'
email = 'admin480@gmail.com'
password = '2030'
user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True, 'is_active': True})
if created:
    user.set_password(password)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    print('Created superuser', username)
else:
    user.set_password(password)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    print('Updated existing superuser', username)
