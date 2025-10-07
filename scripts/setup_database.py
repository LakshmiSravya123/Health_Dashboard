"""Setup database (SQLite by default, or BigQuery/Snowflake if configured)."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.loaders.database_loader import get_loader
from src.utils.logger import log


def main():
    """Setup database tables."""
    log.info("Setting up database...")
    
    loader = get_loader()
    
    # For SQLite, create tables
    if hasattr(loader, 'create_tables'):
        loader.create_tables()
        log.info("✓ Database tables created successfully!")
    else:
        log.info("Using BigQuery - tables will be created on first use")
    
    log.info("Database setup complete!")


if __name__ == "__main__":
    main()
