import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecocash_clone.settings')
import sys

def main():
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = 'admin'
    email = 'admin@gmail.com'
    password = 'admin123@'
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()
    print(f"Superuser {'created' if created else 'updated'}: {username}")

if __name__ == '__main__':
    main()
