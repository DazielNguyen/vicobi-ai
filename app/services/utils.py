import datetime
from datetime import datetime, timezone
import os
import tempfile
from fastapi import UploadFile
from pathlib import Path
from typing import Union
from pydub import AudioSegment


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
    
    @staticmethod
    def convert_audio_to_wav(
        input_file: Union[str, Path],
        output_file: Union[str, Path, None] = None,
        sample_rate: int = 16000,
        channels: int = 1
    ) -> str:
        """
        Chuyển đổi file âm thanh bất kỳ (mp3, aac, m4a, ogg, flac, mp2, v.v.) sang định dạng .wav
        
        Args:
            input_file: Đường dẫn đến file âm thanh đầu vào
            output_file: Đường dẫn đến file .wav đầu ra (nếu None, sẽ tạo file tạm)
            sample_rate: Tần số lấy mẫu (Hz), mặc định 16000 cho speech recognition
            channels: Số kênh âm thanh (1=mono, 2=stereo), mặc định 1
        
        Returns:
            str: Đường dẫn đến file .wav đã chuyển đổi
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File không tồn tại: {input_file}")
        
        if output_file is None:
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"{input_path.stem}_converted.wav")
        
        output_path = Path(output_file)
        
        try:
            audio = AudioSegment.from_file(str(input_path))
            audio = audio.set_frame_rate(sample_rate)
            audio = audio.set_channels(channels)
            
            audio.export(
                str(output_path),
                format="wav",
                parameters=["-ac", str(channels), "-ar", str(sample_rate)]
            )
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Lỗi khi chuyển đổi file âm thanh: {str(e)}")