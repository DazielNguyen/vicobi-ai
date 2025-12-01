from typing import Optional
from .config import Config, load_config
from .voice import BedrockVoiceExtractor
from .bill import BedrockBillExtractor

class BedrockService:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        self.voice_extractor = BedrockVoiceExtractor(self.config)
        self.bill_extractor = BedrockBillExtractor(self.config)

    def is_ready(self) -> bool:
        return self.voice_extractor is not None and self.bill_extractor is not None
    
    def get_model_id(self) -> Optional[str]:
        if self.config:
            return self.config.get('aws.model_id')
        return None

_bedrock_service_instance: Optional[BedrockService] = None

def get_bedrock_service(config: Optional[Config] = None) -> BedrockService:
    """
    Lấy thể hiện singleton của BedrockService
    """
    global _bedrock_service_instance
    
    if _bedrock_service_instance is None:
        _bedrock_service_instance = BedrockService(config)
    
    return _bedrock_service_instance

def reset_bedrock_service() -> None:
    global _bedrock_service_instance
    _bedrock_service_instance = None