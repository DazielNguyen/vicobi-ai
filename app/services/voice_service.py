"""
Service layer for voice/audio processing
"""
from transformers import pipeline
import torch
from typing import Optional
from datetime import datetime
from app.services.transaction_parser import TransactionParser


# Global transcriber instance (lazy loading)
_transcriber = None


def get_transcriber(model_name: str = "vinai/PhoWhisper-small", device: Optional[str] = None):
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


def transcribe_audio_file(wav_file_path: str, model_name: str = "vinai/PhoWhisper-small") -> dict:
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
        
        # Result có thể là dict hoặc list
        if isinstance(result, dict):
            text = result.get("text", "")
        elif isinstance(result, list) and len(result) > 0:
            text = result[0].get("text", "") if isinstance(result[0], dict) else ""
        else:
            text = ""
        
        return {
            "text": text,
            "model": model_name
        }
        
    except Exception as e:
        raise Exception(f"Lỗi khi transcribe audio: {str(e)}")


def parse_transcription_to_voice_data(transcription_text: str) -> dict:
    """
    Parse transcription text thành structured voice data
    SỬ DỤNG TransactionParser để tách nhiều giao dịch
    """
    # Generate unique voice_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    voice_id = f"voice_{timestamp}"
    
    # Parse bằng TransactionParser
    parsed_data = TransactionParser.parse(transcription_text)
    
    return {
        "voice_id": voice_id,
        "total_amount": parsed_data["total_amount"],
        "transactions": parsed_data["transactions"],
        "money_type": "VND",
        "utc_time": datetime.utcnow(),
        "raw_transcription": transcription_text
    }
