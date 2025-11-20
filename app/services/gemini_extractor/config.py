import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self._config: Dict[str, Any] = config_dict or {}
        
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        return self._config.copy()


def load_config(config_path: Optional[Path] = None) -> Config:
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "gemini_config.yaml"
    
    config_dict: Dict[str, Any] = {}
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f) or {}
        except Exception:
            pass
    
    if 'api' not in config_dict:
        config_dict['api'] = {}
    
    env_mappings = {
        'GEMINI_API_KEY': 'api.api_key',
        'GEMINI_MODEL_VERSION': 'api.model_version',
        'GEMINI_TIMEOUT': 'api.timeout',
        'GEMINI_TEMPERATURE': 'api.generation.temperature',
        'GEMINI_MAX_RETRIES': 'api.retry.max_retries',
    }
    
    config = Config(config_dict)
    
    for env_var, config_key in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value:
            if config_key in ['api.timeout', 'api.retry.max_retries']:
                env_value = int(env_value)
            elif config_key == 'api.generation.temperature':
                env_value = float(env_value)
            
            config.set(config_key, env_value)
    
    if not config.get('api.api_key'):
        raise ValueError("GEMINI_API_KEY is required")
    
    return config
