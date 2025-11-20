from transformers import pipeline
import torch
from typing import Optional
from datetime import datetime
from app.services.gemini_extractor.gemini_service import get_gemini_service

_transcriber = None

def get_transcriber(model_name: str = "vinai/PhoWhisper-small", device: Optional[str] = None):
    """
    Get PhoWhisper transcriber instance
    """
    global _transcriber
    
    if _transcriber is None:
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            _transcriber = pipeline(
                "automatic-speech-recognition",
                model=model_name,
                device=device
            )

        except Exception as e:
            raise
    
    return _transcriber

def transcribe_audio_file(wav_file_path: str, model_name: str = "vinai/PhoWhisper-small") -> dict:
    """
    Transcribe audio file using PhoWhisper model
    
    Args:
        wav_file_path: Path to WAV audio file
        model_name: PhoWhisper model name
        
    Returns:
        Dictionary with transcribed text and model name
    """
    try:
        transcriber = get_transcriber(model_name=model_name)
        result = transcriber(wav_file_path)
        
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
    Parse transcription text using Gemini to extract transaction data
    
    Args:
        transcription_text: Text from PhoWhisper transcription
        
    Returns:
        Dictionary containing voice_id, total_amount, transactions, money_type, utc_time, raw_transcription
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    voice_id = f"voice_{timestamp}"
    
    # Use Gemini to extract transaction data from transcription
    gemini_service = get_gemini_service()
    
    # Log the transcription being processed
    print(f"[DEBUG] Transcription text: {transcription_text}")
    
    parsed_data = gemini_service.extract_voice_data(transcription_text)
    
    # Log the parsed result
    print(f"[DEBUG] Parsed data from Gemini: {parsed_data}")
    
    return {
        "voice_id": voice_id,
        "total_amount": parsed_data["total_amount"],
        "transactions": parsed_data["transactions"],
        "money_type": parsed_data.get("money_type", "VND"),
        "utc_time": datetime.utcnow(),
        "raw_transcription": transcription_text
    }
