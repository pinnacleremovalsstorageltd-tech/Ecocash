# EcoCash Partner Portal - Installation & Setup Guide

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment support (venv)

## 🚀 Quick Start

### Windows

1. **Install Python** (if not already installed)
   - Download from https://www.python.org/downloads/
   - **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify installation: `python --version`

2. **Run the setup script**
   ```bash
   setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Run database migrations
   - Create logs directory

3. **Create a superuser (admin account)**
   ```bash
   .venv\Scripts\activate.bat
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account

4. **Start the development server**
   ```bash
   python manage.py runserver
   ```

5. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - Login with the superuser credentials you created

### Linux/macOS

1. **Install Python** (if not already installed)
   ```bash
   # macOS (using Homebrew)
   brew install python3

   # Ubuntu/Debian
   sudo apt-get install python3 python3-venv python3-pip
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Create a superuser**
   ```bash
   source .venv/bin/activate
   python manage.py createsuperuser
   ```

4. **Start the development server**
   ```bash
   python manage.py runserver
   ```

5. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 📁 Project Structure

```
ecocash_clone/
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .gitignore                 # Git ignore file
├── docker-compose.yml         # Docker setup
├── Dockerfile                 # Docker image definition
├── setup.bat                  # Windows setup script
├── setup.sh                   # Linux/macOS setup script
│
├── ecocash_clone/             # Main project package
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL routing
│   ├── wsgi.py                # WSGI application
│   ├── asgi.py                # ASGI application
│   └── celery.py              # Celery task queue
│
├── accounts/                  # User authentication & management
│   ├── models.py              # User, Partner, Activity models
│   ├── views.py               # Authentication views
│   ├── forms.py               # Registration, login forms
│   ├── urls.py                # Account URLs
│   ├── admin.py               # Admin interface
│   ├── middleware.py          # Custom middleware
│   ├── decorators.py          # Custom decorators
│   ├── utils.py               # Helper functions
│   └── context_processors.py  # Template context
│
├── dashboard/                 # Dashboard & reporting
│   ├── views.py
│   ├── urls.py
│   └── models.py
│
├── applications/              # Application management
│   ├── views.py
│   ├── urls.py
│   └── models.py
│
├── payments/                  # Payment processing
│   ├── views.py
│   ├── urls.py
│   └── models.py
│
├── core/                      # Core functionality
│   ├── models.py              # BaseModel, Address, Document
│   ├── admin.py               # Base admin class
│   └── context_processors.py  # Global context
│
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   ├── accounts/              # Auth templates
│   └── dashboard/             # Dashboard templates
│
├── static/                    # Static files (CSS, JS)
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                     # User uploads
└── logs/                      # Application logs
```

## 🔧 Available Commands

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Create a superuser account
python manage.py createsuperuser

# Run the development server
python manage.py runserver

# Collect static files (production)
python manage.py collectstatic

# Run tests
python manage.py test

# Access Django shell
python manage.py shell

# Create an app
python manage.py startapp app_name
```

## 📊 Default Credentials

After setup:
1. Create superuser with `python manage.py createsuperuser`
2. Login at http://localhost:8000/admin with the credentials you created

## 🌐 Application Features

### Authentication
- User registration with email verification
- Login with username/email
- Password reset via email
- Account lockout after failed attempts
- Security questions
- Two-factor authentication ready

### User Management
- Partner profiles with tiers
- Document upload & verification
- Activity logging
- User notifications
- Session management

### Dashboard
- Partner overview
- Application management
- Payment tracking
- Reporting

### Admin Panel
- User management
- Partner management
- Activity monitoring
- Document verification
- System health checks

## 🔐 Security Features

- CSRF protection
- XSS prevention
- SQL injection protection
- Password hashing (PBKDF2)
- Rate limiting ready
- Secure session management
- Account lockout mechanism
- Activity audit logging

## 📦 Dependencies

See `requirements.txt` for all dependencies. Key packages:
- Django 4.2.0
- Django REST Framework
- Celery (task queue)
- PostgreSQL support
- Django Admin Extensions
- Authentication & authorization

## 🐳 Docker Deployment

To run with Docker:

```bash
docker-compose up --build
```

This will:
- Build the Django app
- Start PostgreSQL database
- Start the web server on port 8000

Access at http://localhost:8000

## 🆘 Troubleshooting

### Python not found
- Ensure Python 3.11+ is installed
- Add Python to your system PATH
- Verify with `python --version`

### Port 8000 already in use
```bash
python manage.py runserver 8001
```

### Database errors
```bash
# Reset migrations
python manage.py migrate accounts zero
python manage.py migrate

# Create fresh database
rm db.sqlite3
python manage.py migrate
```

### Missing dependencies
```bash
pip install --upgrade -r requirements.txt
```

## 📝 Environment Variables

Edit `.env` to configure:
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains
- `DATABASE_URL`: Database connection string
- `EMAIL_BACKEND`: Email service configuration
- `REDIS_URL`: Redis cache connection
- `SECRET_KEY`: Django secret key (change in production)

## 🚀 Deployment

For production:
1. Set `DEBUG=False` in `.env`
2. Update `ALLOWED_HOSTS` with your domain
3. Use PostgreSQL instead of SQLite
4. Set up proper email backend
5. Use environment-based `SECRET_KEY`
6. Configure HTTPS/SSL
7. Use Gunicorn as application server
8. Set up Nginx as reverse proxy

## 📞 Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Review Django error messages
3. Check database migrations
4. Verify all dependencies are installed

## ✅ What's Included

✅ Complete user authentication system
✅ Partner profile management
✅ Document verification workflow
✅ Activity logging & auditing
✅ Admin interface
✅ REST API ready
✅ Email notification system
✅ Security features (lockout, rate limiting, etc.)
✅ Responsive Bootstrap templates
✅ Docker support
✅ Production-ready configuration

## 📄 License

This is a clone project for educational purposes.

---

**Ready to get started?** Run `setup.bat` (Windows) or `setup.sh` (Linux/macOS) now!
