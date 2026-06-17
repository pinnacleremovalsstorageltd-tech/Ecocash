import sqlite3
import os
DB = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
DB = os.path.abspath(DB)
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT app, name, applied FROM django_migrations ORDER BY app, applied")
for row in cur.fetchall():
    print(row)
conn.close()
