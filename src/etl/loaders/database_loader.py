"""Unified database loader supporting multiple warehouses."""

from src.utils.config_loader import get_config
from src.utils.logger import log


def get_loader():
    """Get the appropriate database loader based on configuration.
    
    Returns:
        Database loader instance (BigQueryLoader or SQLiteLoader)
    """
    config = get_config()
    warehouse_type = config.config.get('warehouse_type', 'sqlite')
    
    if warehouse_type == 'bigquery':
        bigquery_config = config.config.get('bigquery', {})
        if bigquery_config.get('enabled', False):
            from src.etl.loaders.bigquery_loader import BigQueryLoader
            log.info("Using BigQuery as data warehouse")
            return BigQueryLoader()
        else:
            log.warning("BigQuery not enabled, falling back to SQLite")
            warehouse_type = 'sqlite'
    
    if warehouse_type == 'snowflake':
        snowflake_config = config.config.get('snowflake', {})
        if snowflake_config.get('enabled', False):
            # TODO: Implement Snowflake loader
            log.warning("Snowflake not yet implemented, falling back to SQLite")
            warehouse_type = 'sqlite'
    
    # Default to SQLite (free option)
    from src.etl.loaders.sqlite_loader import SQLiteLoader
    log.info("Using SQLite as data warehouse (100% FREE)")
    return SQLiteLoader()
