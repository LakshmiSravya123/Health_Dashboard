"""Configuration loader utility for the Mental Health Dashboard."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ConfigLoader:
    """Load and manage application configuration."""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration loader.
        
        Args:
            config_path: Path to config.yaml file. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._substitute_env_vars(self.config)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _substitute_env_vars(self, config: Dict[str, Any]) -> None:
        """Recursively substitute environment variables in config.
        
        Replaces ${VAR_NAME} with the value of environment variable VAR_NAME.
        """
        for key, value in config.items():
            if isinstance(value, dict):
                self._substitute_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var, value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._substitute_env_vars(item)
                    elif isinstance(item, str) and item.startswith("${") and item.endswith("}"):
                        env_var = item[2:-1]
                        value[i] = os.getenv(env_var, item)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to config value (e.g., 'bigquery.project_id')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_bigquery_config(self) -> Dict[str, Any]:
        """Get BigQuery configuration."""
        return self.config.get('bigquery', {})
    
    def get_data_sources_config(self) -> Dict[str, Any]:
        """Get data sources configuration."""
        return self.config.get('data_sources', {})
    
    def get_sentiment_config(self) -> Dict[str, Any]:
        """Get sentiment analysis configuration."""
        return self.config.get('sentiment_analysis', {})
    
    def get_burnout_config(self) -> Dict[str, Any]:
        """Get burnout prediction configuration."""
        return self.config.get('burnout_prediction', {})
    
    def get_alert_config(self) -> Dict[str, Any]:
        """Get alert system configuration."""
        return self.config.get('alerts', {})
    
    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard configuration."""
        return self.config.get('dashboard', {})


# Global config instance
_config_instance = None


def get_config() -> ConfigLoader:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader()
    return _config_instance
