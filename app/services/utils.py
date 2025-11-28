import datetime
from datetime import datetime, timezone
import os
import tempfile
from fastapi import UploadFile


class Utils:
    @staticmethod
    def is_valid_image_file(filename: str) -> bool:
        """Kiểm tra định dạng file hình ảnh hợp lệ"""
        if not filename:
            return False
        valid_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"]
        return any(filename.lower().endswith(ext) for ext in valid_extensions)
    
    @staticmethod
    def is_valid_audio_file(filename: str) -> bool:
        """Kiểm tra định dạng file âm thanh hợp lệ"""
        if not filename:
            return False
        valid_extensions = [".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"]
        return any(filename.lower().endswith(ext) for ext in valid_extensions)
    
    @staticmethod
    def save_temp_file(file: UploadFile, content: bytes) -> str:
        """Lưu file tải lên vào thư mục tạm thời"""
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"input_{file.filename}")
        
        with open(temp_path, "wb") as buffer:
            buffer.write(content)
        
        return temp_path
    
    @staticmethod
    def remove_temp_file(file_path: str):
        """Xóa file tạm thời"""
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def generate_unique_filename(prefix: str, original_filename: str) -> str:
        """Tạo tên file duy nhất dựa trên tên gốc và timestamp"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        name, ext = os.path.splitext(original_filename)
        unique_filename = f"{prefix}_{name}_{timestamp}{ext}"
        return unique_filename