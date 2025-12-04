from langchain_huggingface import HuggingFaceEmbeddings
from typing import Optional
import threading
from loguru import logger

_model_lock = threading.Lock()
_embedding_model = None

def get_embedding_model(model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device: Optional[str] = None):
    """Get HuggingFace Embedding model instance (Singleton and Thread-safe initialization)"""
    global _embedding_model
    
    if _embedding_model is None:
        with _model_lock:
            if _embedding_model is None:
                if device is None:
                    device = "cpu"
                                
                try:
                    _embedding_model = HuggingFaceEmbeddings(
                        model_name=model_name,
                        model_kwargs={'device': device},
                        encode_kwargs={'normalize_embeddings': True}
                    )

                except Exception as e:
                    logger.error(f"Error loading Embedding model: {str(e)}")
                    raise e
    
    return _embedding_model

def is_embedding_model_ready() -> bool:
    """Kiểm tra xem embedding model đã được tải chưa"""
    return _embedding_model is not None

def get_embedding_dimension() -> int:
    """Trả về dimension của model (MiniLM-L12-v2 là 384)"""
    return 384