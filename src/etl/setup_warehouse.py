"""Setup BigQuery data warehouse schema."""

import json
from pathlib import Path
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from src.utils.config_loader import get_config
from src.utils.logger import log


class WarehouseSetup:
    """Setup and manage BigQuery data warehouse."""
    
    def __init__(self):
        """Initialize warehouse setup."""
        self.config = get_config()
        bq_config = self.config.get_bigquery_config()
        
        self.project_id = bq_config.get('project_id')
        self.dataset_id = bq_config.get('dataset_id')
        self.location = bq_config.get('location', 'US')
        
        self.client = bigquery.Client(project=self.project_id)
        
        # Load schema definitions
        schema_path = Path(__file__).parent.parent.parent / "config" / "bigquery_schema.json"
        with open(schema_path, 'r') as f:
            self.schemas = json.load(f)
    
    def create_dataset(self) -> None:
        """Create BigQuery dataset if it doesn't exist."""
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.client.get_dataset(dataset_ref)
            log.info(f"Dataset {dataset_ref} already exists")
        except NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = self.location
            dataset.description = "Mental Health Analytics Data Warehouse"
            
            dataset = self.client.create_dataset(dataset, timeout=30)
            log.info(f"Created dataset {dataset_ref}")
    
    def create_table(self, table_name: str) -> None:
        """Create a BigQuery table with schema from config.
        
        Args:
            table_name: Name of the table to create
        """
        if table_name not in self.schemas:
            raise ValueError(f"Schema not found for table: {table_name}")
        
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        table_config = self.schemas[table_name]
        
        try:
            self.client.get_table(table_ref)
            log.info(f"Table {table_ref} already exists")
            return
        except NotFound:
            pass
        
        # Create table schema
        schema = self._build_schema(table_config['schema'])
        
        table = bigquery.Table(table_ref, schema=schema)
        table.description = table_config.get('description', '')
        
        # Add time partitioning if specified
        if 'time_partitioning' in table_config:
            partition_config = table_config['time_partitioning']
            table.time_partitioning = bigquery.TimePartitioning(
                type_=getattr(bigquery.TimePartitioningType, partition_config['type']),
                field=partition_config.get('field')
            )
        
        # Add clustering if specified
        if 'clustering' in table_config:
            table.clustering_fields = table_config['clustering']
        
        table = self.client.create_table(table)
        log.info(f"Created table {table_ref}")
    
    def _build_schema(self, schema_config: list) -> list:
        """Build BigQuery schema from configuration.
        
        Args:
            schema_config: Schema configuration from JSON
            
        Returns:
            List of SchemaField objects
        """
        schema = []
        
        for field_config in schema_config:
            field_type = field_config['type']
            field_mode = field_config.get('mode', 'NULLABLE')
            
            # Handle nested fields (RECORD type)
            if field_type == 'RECORD' and 'fields' in field_config:
                nested_fields = self._build_schema(field_config['fields'])
                field = bigquery.SchemaField(
                    field_config['name'],
                    field_type,
                    mode=field_mode,
                    description=field_config.get('description', ''),
                    fields=nested_fields
                )
            else:
                field = bigquery.SchemaField(
                    field_config['name'],
                    field_type,
                    mode=field_mode,
                    description=field_config.get('description', '')
                )
            
            schema.append(field)
        
        return schema
    
    def setup_all_tables(self) -> None:
        """Create dataset and all tables."""
        log.info("Starting warehouse setup...")
        
        # Create dataset
        self.create_dataset()
        
        # Create all tables
        for table_name in self.schemas.keys():
            self.create_table(table_name)
        
        log.info("Warehouse setup completed successfully")
    
    def drop_table(self, table_name: str) -> None:
        """Drop a table (use with caution).
        
        Args:
            table_name: Name of the table to drop
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        try:
            self.client.delete_table(table_ref)
            log.warning(f"Dropped table {table_ref}")
        except NotFound:
            log.warning(f"Table {table_ref} not found")


def main():
    """Main function to setup warehouse."""
    setup = WarehouseSetup()
    setup.setup_all_tables()


if __name__ == "__main__":
    main()
