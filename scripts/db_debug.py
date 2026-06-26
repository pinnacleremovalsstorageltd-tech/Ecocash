import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db.sqlite3'
OUT_PATH = BASE_DIR / 'scripts' / 'db_debug_output.txt'

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    cur.execute("PRAGMA table_info('accounts_loginlog')")
    log_cols = [r[1] for r in cur.fetchall()]
    cur.execute("SELECT app, name FROM django_migrations WHERE app='accounts' ORDER BY id")
    migrations = [f"{r[0]}:{r[1]}" for r in cur.fetchall()]

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write('tables:\n')
    f.write('\n'.join(tables) + '\n')
    f.write('\naccounts_loginlog columns:\n')
    f.write('\n'.join(log_cols) + '\n')
    f.write('\naccounts migrations:\n')
    f.write('\n'.join(migrations) + '\n')

print('wrote', OUT_PATH)
