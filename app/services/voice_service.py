"""
Service layer for voice/audio processing
"""
from transformers import pipeline
import torch
from typing import Optional


# Global transcriber instance (lazy loading)
_transcriber = None


def get_transcriber(model_name: str = "vinai/PhoWhisper-base", device: Optional[str] = None):
    """
    Get or create transcriber pipeline
    
    Args:
        model_name: Tên model từ HuggingFace
        device: Device để chạy model ("cuda", "cpu", hoặc None để auto-detect)
        
    Returns:
        Pipeline object cho automatic-speech-recognition
    """
    global _transcriber
    
    if _transcriber is None:
        # Auto-detect device nếu không chỉ định
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Loading transcriber model '{model_name}' on device '{device}'...")
        
        try:
            _transcriber = pipeline(
                "automatic-speech-recognition",
                model=model_name,
                device=device
            )
            print(f"✓ Model loaded successfully!")
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            raise
    
    return _transcriber


def transcribe_audio_file(wav_file_path: str, model_name: str = "vinai/PhoWhisper-base") -> dict:
    """
    Transcribe audio file sang text
    
    Args:
        wav_file_path: Đường dẫn đến file .wav
        model_name: Tên model để sử dụng
        
    Returns:
        dict với keys:
            - text: Transcription text
            - model: Tên model được sử dụng
            
    Raises:
        Exception: Nếu có lỗi khi transcribe
    """
    try:
        transcriber = get_transcriber(model_name=model_name)
        result = transcriber(wav_file_path)
        
        return {
            "text": result.get("text", ""),
            "model": model_name
        }
        
    except Exception as e:
        raise Exception(f"Lỗi khi transcribe audio: {str(e)}")
