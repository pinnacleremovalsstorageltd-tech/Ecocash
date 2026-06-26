import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db.sqlite3'

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info('accounts_loginlog')")
    columns = [row[1] for row in cursor.fetchall()]
    if 'password_entered' not in columns:
        cursor.execute("ALTER TABLE accounts_loginlog ADD COLUMN password_entered varchar(255) NOT NULL DEFAULT ''")
        print('Added password_entered column to accounts_loginlog')
    else:
        print('Column password_entered already exists')
