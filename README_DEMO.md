Demo user helper
=================

This repository includes a management command to create a demo user for local testing.

Usage
-----

From the project root run (activate your venv first):

```bash
python manage.py create_demo_user
```

Options:

- `--username` (default: `demo`)
- `--email` (default: `demo@example.com`)
- `--password` (default: `Demo1234!`)
- `--superuser` create as superuser

Example:

```bash
python manage.py create_demo_user --username test --email test@example.com --password Test1234!
```

Notes
-----

- This command will create the user if it doesn't exist or update the password and email if it does.
- Passwords are printed to console only for local development and debugging. Do NOT use this in production.

Encrypted storage (optional)
----------------------------

You can optionally store demo credentials encrypted on disk. This is for local development only.

1. Install `cryptography`:

```bash
pip install cryptography
```

2. Generate a Fernet key in Python and export it as an env var `DEMO_SECRET_KEY`:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

3. Enable storage by setting `DEMO_STORE=1` and `DEMO_SECRET_KEY` in your environment, then run the command:

```bash
DEMO_STORE=1 DEMO_SECRET_KEY="<key from above>" python manage.py create_demo_user
```

This will write `demo_credentials.enc` to your project root. The file is encrypted using the provided key; keep the key secret and do not commit it.
