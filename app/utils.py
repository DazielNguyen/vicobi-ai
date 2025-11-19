import os
import tempfile
from pathlib import Path
from typing import Union
from pydub import AudioSegment


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
        
    Raises:
        FileNotFoundError: Nếu file đầu vào không tồn tại
        Exception: Nếu có lỗi trong quá trình chuyển đổi
        
    Example:
        >>> wav_path = convert_audio_to_wav("audio.mp3")
        >>> wav_path = convert_audio_to_wav("audio.aac", "output.wav", sample_rate=22050)
    """
    input_path = Path(input_file)
    
    # Kiểm tra file đầu vào có tồn tại không
    if not input_path.exists():
        raise FileNotFoundError(f"File không tồn tại: {input_file}")
    
    # Nếu không chỉ định output_file, tạo file tạm
    if output_file is None:
        temp_dir = tempfile.gettempdir()
        output_file = os.path.join(temp_dir, f"{input_path.stem}_converted.wav")
    
    output_path = Path(output_file)
    
    try:
        # Đọc file âm thanh (pydub tự động detect format)
        audio = AudioSegment.from_file(str(input_path))
        
        # Chuyển đổi về sample rate và số kênh mong muốn
        audio = audio.set_frame_rate(sample_rate)
        audio = audio.set_channels(channels)
        
        # Export sang .wav
        audio.export(
            str(output_path),
            format="wav",
            parameters=["-ac", str(channels), "-ar", str(sample_rate)]
        )
        
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Lỗi khi chuyển đổi file âm thanh: {str(e)}")
