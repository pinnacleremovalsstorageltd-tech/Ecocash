from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os
import json

try:
    from cryptography.fernet import Fernet
    _HAS_CRYPTO = True
except Exception:
    _HAS_CRYPTO = False


class Command(BaseCommand):
    help = 'Create or update a demo user for local testing. Prints credentials to console.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='demo', help='Demo username')
        parser.add_argument('--email', default='demo@example.com', help='Demo email')
        parser.add_argument('--password', default='Demo1234!', help='Demo password')
        parser.add_argument('--superuser', action='store_true', help='Create as superuser')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password']
        make_super = options['superuser']

        try:
            user = User.objects.filter(username=username).first()
            if user:
                user.email = email
                user.is_active = True
                if make_super:
                    user.is_staff = True
                    user.is_superuser = True
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Updated existing demo user: {username}'))
            else:
                if make_super:
                    user = User.objects.create_superuser(username=username, email=email, password=password)
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'Created demo user: {username}'))

            self.stdout.write('--- Demo credentials ---')
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write('You can log in at /accounts/login/ or via the admin at /admin/')
            # Optionally store encrypted demo credentials locally for development.
            if os.environ.get('DEMO_STORE') == '1':
                if not _HAS_CRYPTO:
                    self.stderr.write(self.style.ERROR('cryptography package not available. Install with `pip install cryptography` to use DEMO_STORE.'))
                else:
                    key = os.environ.get('DEMO_SECRET_KEY')
                    if not key:
                        self.stderr.write(self.style.ERROR('DEMO_SECRET_KEY not set. Set an env var with Fernet key to enable storage.'))
                    else:
                        try:
                            f = Fernet(key.encode() if isinstance(key, str) else key)
                            payload = json.dumps({'username': username, 'email': email, 'password': password}).encode()
                            token = f.encrypt(payload)
                            out_path = os.path.join(getattr(settings, 'BASE_DIR', '.'), 'demo_credentials.enc')
                            with open(out_path, 'wb') as fh:
                                fh.write(token)
                            self.stdout.write(self.style.SUCCESS(f'Encrypted demo credentials written to: {out_path}'))
                        except Exception as exc:
                            self.stderr.write(self.style.ERROR(f'Failed to encrypt/store demo credentials: {exc}'))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'Error creating demo user: {exc}'))
