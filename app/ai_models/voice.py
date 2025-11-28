from transformers import pipeline
import torch
from typing import Optional

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