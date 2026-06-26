#!/usr/bin/env python
"""Script to set up test users and verify login tracking."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecocash_clone.settings')
django.setup()

from accounts.models import User, LoginLog
from django.contrib.auth.hashers import make_password

# Set admin password
admin = User.objects.get(username='admin480')
admin.set_password('2030')
admin.save()
print(f"✓ Admin password set: admin480 / 2030")

# Create a test user
test_user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'testuser@test.com',
        'first_name': 'Test',
        'last_name': 'User',
        'is_active': True,
        'account_status': 'active',
        'user_type': 'partner'
    }
)
test_user.set_password('testpass123')
test_user.save()
print(f"✓ Test user created: testuser / testpass123" if created else f"✓ Test user exists: testuser / testpass123")

# Check current login logs
logs = LoginLog.objects.all()
print(f"\n✓ Total login logs in database: {logs.count()}")
if logs.exists():
    print("\nRecent login attempts:")
    for log in logs.order_by('-timestamp')[:5]:
        print(f"  - {log.username_attempted} | Success: {log.success} | IP: {log.ip_address} | {log.timestamp}")
else:
    print("  (No logs yet - will appear after login test)")

print("\n✓ Setup complete! Ready for login testing.")
print("\nTo test:")
print("1. Go to http://127.0.0.1:8000/login/")
print("2. Try logging in with: testuser / testpass123")
print("3. Check admin at http://127.0.0.1:8000/admin/")
print("   - Login with: admin480 / 2030")
print("   - Navigate to 'Login Logs' to see tracked attempts")
