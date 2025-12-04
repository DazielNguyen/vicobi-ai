from typing import Any, Dict, Optional
from app.config import settings 

class Config:
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self._config: Dict[str, Any] = config_dict or {}
        
    def get(self, key: str, default: Any = None) -> Any:
        """Hỗ trợ lấy value theo key dạng dot notation: 'aws.region'"""
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

def load_config() -> Config:
    """Load configuration from Pydantic Settings"""
    config_dict = {
        "aws": {
            "region": settings.AWS_REGION,
            "model_id": settings.BEDROCK_MODEL_ID,
            "timeout": settings.BEDROCK_TIMEOUT,
            "access_key_id": settings.AWS_ACCESS_KEY_ID,
            "secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "generation": {
                "temperature": settings.BEDROCK_TEMPERATURE
            }
        }
    }
    
    return Config(config_dict)