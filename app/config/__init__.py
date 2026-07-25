"""
Configuration management service
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigService:
    """Centralized configuration management"""
    
    def __init__(self):
        self._config = {}
        self._config_path = Path("config.yaml")
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            if self._config_path.exists():
                with open(self._config_path, 'r') as f:
                    self._config = yaml.safe_load(f)
                print("✅ Configuration loaded successfully")
            else:
                print("⚠️ Config file not found, using defaults")
                self._config = {}
        except Exception as e:
            print(f"❌ Config loading failed: {e}")
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        return self.get('ai', {})
    
    def get_anthropic_config(self) -> Dict[str, Any]:
        """Get Anthropic configuration"""
        return self.get('ai.anthropic', {})
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get provider-specific configuration"""
        return self.get(f'ai.{provider}', {})
    
    def is_anthropic_available(self) -> bool:
        """Check if Anthropic API key is available"""
        return bool(os.environ.get('ANTHROPIC_API_KEY'))
    
    def get_anthropic_models(self) -> Dict[str, str]:
        """Get Anthropic model configuration"""
        anthropic_config = self.get_anthropic_config()
        return {
            'default': anthropic_config.get('default_model', 'claude-3-haiku-20240307'),
            'backup': anthropic_config.get('backup_model', 'claude-3-haiku-20240307')
        }
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()

# Global config instance
config = ConfigService()