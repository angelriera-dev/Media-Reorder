import os
import sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from CLI.db import get_db

target_db_path = Path("tests/reorder/reorder.db")

print(f"Creating DB at: {target_db_path.absolute()}")

# Initialize DB
conn = get_db(target_db_path)
conn.close()

# Verify existence
if target_db_path.exists():
    print("SUCCESS: Database file created at specified path.")
else:
    print("FAILURE: Database file NOT found at specified path.")
    sys.exit(1)
