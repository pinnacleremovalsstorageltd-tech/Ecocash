import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecocash_clone.settings')

from django.core.management import call_command
from django import setup

setup()

out_file = BASE_DIR / 'scripts' / 'run_migrate_output.txt'
with open(out_file, 'w', encoding='utf-8') as f:
    try:
        call_command('migrate', 'accounts', stdout=f, stderr=f, verbosity=2)
    except Exception as e:
        f.write(f'EXCEPTION: {e}\n')

print(f'Wrote {out_file}')
