from transformers import pipeline
import torch
from typing import Optional
import threading
import os

_model_lock = threading.Lock()
_transcriber = None

def get_transcriber(model_name: str = "vinai/PhoWhisper-small", device: Optional[str] = None):
    """
    Get PhoWhisper transcriber instance (Singleton & Thread-safe initialization)
    """
    global _transcriber
    
    # Double-check locking pattern để an toàn khi init
    if _transcriber is None:
        with _model_lock:
            if _transcriber is None:
                if device is None:
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                
                print(f"--- Đang tải model {model_name} trên thiết bị: {device} ---")
                
                # Cấu hình tối ưu RAM
                model_kwargs = {
                    "low_cpu_mem_usage": True  # <--- CỰC KỲ QUAN TRỌNG: Giảm RAM spike khi load
                }

                # Nếu chạy GPU, dùng float16 để giảm 50% VRAM
                if device == "cuda":
                    model_kwargs["torch_dtype"] = torch.float16
                else:
                    # Trên CPU Fargate, float32 ổn định hơn float16 (một số CPU cũ không hỗ trợ tốt float16)
                    model_kwargs["torch_dtype"] = torch.float32 

                try:
                    _transcriber = pipeline(
                        "automatic-speech-recognition",
                        model=model_name,
                        device=device,
                        model_kwargs=model_kwargs # Inject cấu hình tối ưu vào
                    )
                    print("--- Tải model thành công ---")

                except Exception as e:
                    print(f"--- Lỗi tải model: {str(e)} ---")
                    raise e
    
    return _transcriber

def transcribe_audio_file(wav_file_path: str, model_name: str = "vinai/PhoWhisper-small") -> dict:
    """
    Transcribe audio file using PhoWhisper model
    """
    try:
        # Lấy instance (đã cache)
        transcriber = get_transcriber(model_name=model_name)
        
        # 2. Critical Section: Chỉ cho phép 1 request chạy xử lý Voice tại 1 thời điểm
        # Nếu không có Lock này, 2 users gọi cùng lúc sẽ làm container crash vì hết RAM.
        with _model_lock:
            # batch_size=1 để an toàn nhất về RAM
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