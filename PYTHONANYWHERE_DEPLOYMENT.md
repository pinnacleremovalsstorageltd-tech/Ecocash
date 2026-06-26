# PythonAnywhere Deployment Guide

## 1. Create a PythonAnywhere account
1. Sign in to https://www.pythonanywhere.com
2. Create a new web app under your account
3. Choose `Manual configuration` and `Python 3.11`

## 2. Upload your repository
1. Use the PythonAnywhere **Files** page to upload your project ZIP, or
2. Clone directly from GitHub:
   ```bash
   cd ~
   git clone https://github.com/pinnacleremovalsstorageltd-tech/Ecocash.git
   cd Ecocash
   ```

## 3. Create and activate a virtualenv
```bash
python3.11 -m venv ~/.virtualenvs/ecocash
source ~/.virtualenvs/ecocash/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure environment variables
Create a `.env` file in the project root with values from `.env.example`.

Example:
```ini
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
DATABASE_URL=sqlite:///db.sqlite3
TIME_ZONE=Africa/Harare
SITE_NAME=EcoCash Partner Portal
SITE_URL=https://yourusername.pythonanywhere.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@ecocash.co.zw
```

## 5. Update `ALLOWED_HOSTS`
In `ecocash_clone/settings.py`, set:
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='yourusername.pythonanywhere.com', cast=Csv())
```

## 6. Collect static files
```bash
python manage.py collectstatic --noinput
```

## 7. Run migrations
```bash
python manage.py migrate
```

## 8. Create a superuser
```bash
python manage.py createsuperuser
```

## 9. Configure the PythonAnywhere web app
On the PythonAnywhere Web tab:
- Set the Working directory to `/home/yourusername/Ecocash`
- Set the Virtualenv path to `/home/yourusername/.virtualenvs/ecocash`
- Set the WSGI configuration file to the provided path

Edit the WSGI file to point to your project:
```python
import os
import sys
sys.path.insert(0, '/home/yourusername/Ecocash')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecocash_clone.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 10. Refresh the web app
After saving, hit **Reload** on the PythonAnywhere Web tab.

## 11. Optional: enable SSL
PythonAnywhere provides HTTPS automatically on your subdomain.

## 12. Troubleshooting
- Use the `error log` on the Web tab for Python errors
- Use `access log` for request diagnostics
- Verify `ALLOWED_HOSTS`, `STATIC_ROOT`, and `.env` values

## 13. Notes
- This project uses `whitenoise` for static file serving
- The default database is SQLite; for production, consider PostgreSQL
- Ensure `DEBUG=False` in production
