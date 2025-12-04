from transformers import pipeline
import torch
from typing import Optional
import threading

_model_lock = threading.Lock()
_transcriber = None

def get_transcriber(model_name: str = "vinai/PhoWhisper-small", device: Optional[str] = None):
    """Get PhoWhisper transcriber instance (Singleton and Thread-safe initialization)"""
    global _transcriber
    
    if _transcriber is None:
        with _model_lock:
            if _transcriber is None:
                if device is None:
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                
                print(f"Loading model {model_name} on device: {device}")
                
                model_kwargs = {
                    "low_cpu_mem_usage": True
                }

                if device == "cuda":
                    model_kwargs["torch_dtype"] = torch.float16
                else:
                    model_kwargs["torch_dtype"] = torch.float32 

                try:
                    _transcriber = pipeline(
                        "automatic-speech-recognition",
                        model=model_name,
                        device=device,
                        model_kwargs=model_kwargs 
                    )
                    print("Model loaded successfully")

                except Exception as e:
                    print(f"Error loading model: {str(e)}")
                    raise e
    
    return _transcriber

def is_transcriber_ready() -> bool:
    """Kiểm tra xem transcriber đã được tải chưa"""
    return _transcriber is not None

def transcribe_audio_file(wav_file_path: str, model_name: str = "vinai/PhoWhisper-small") -> dict:
    """
    Transcribe audio file using PhoWhisper model
    """
    try:
        transcriber = get_transcriber(model_name=model_name)
        
        with _model_lock:
            result = transcriber(wav_file_path, batch_size=1)
        
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
        print(f"CRITICAL ERROR in transcribe: {str(e)}")
        raise Exception(f"Lỗi khi transcribe audio: {str(e)}")