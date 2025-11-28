from typing import Optional
from .config import Config, load_config
from app.services.gemini_extractor.voice import GeminiVoiceExtractor
from app.services.gemini_extractor.bill import GeminiBillExtractor


class GeminiService:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        self.voice_extractor = GeminiVoiceExtractor(self.config)
        self.bill_extractor = GeminiBillExtractor(self.config)

    def is_ready(self) -> bool:
        return self.voice_extractor is not None and self.bill_extractor is not None
    
    def get_model_version(self) -> Optional[str]:
        if self.config:
            return self.config.get('api.model_version')
        return None


_gemini_service_instance: Optional[GeminiService] = None

def get_gemini_service(config: Optional[Config] = None) -> GeminiService:
    """
    Lấy thể hiện singleton của GeminiService
    """
    global _gemini_service_instance
    
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService(config)
    
    return _gemini_service_instance


def reset_gemini_service() -> None:
    """Đặt lại thể hiện singleton của dịch vụ (hữu ích cho việc kiểm thử)"""
    global _gemini_service_instance
    _gemini_service_instance = None
