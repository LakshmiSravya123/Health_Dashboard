"""Reset the database (clear all data)."""

import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import log


def main():
    """Reset the database."""
    db_path = Path(__file__).parent.parent / "data" / "mental_health.db"
    
    if db_path.exists():
        response = input(f"⚠️  This will delete {db_path}. Continue? (yes/no): ")
        if response.lower() == 'yes':
            os.remove(db_path)
            log.info(f"✓ Database deleted: {db_path}")
            log.info("Run 'python scripts/run_full_pipeline.py' to recreate with fresh data")
        else:
            log.info("Cancelled")
    else:
        log.info("Database does not exist")


if __name__ == "__main__":
    main()
