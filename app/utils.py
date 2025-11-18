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


def format_vnd_general(amount: float) -> str:
    """
    Chuyển đổi số tiền (VND) sang dạng rút gọn tiếng Việt.
    Hỗ trợ từ đơn vị đồng -> nghìn -> triệu -> tỷ -> nghìn tỷ -> triệu tỷ
    
    Ví dụ:
        500 -> '500 đồng'
        15_000 -> '15 nghìn'
        550_000 -> '550 nghìn'
        1_250_000 -> '1,25 triệu'
        50_000_000 -> '50 triệu'
        2_000_000_000 -> '2 tỷ'
        1_500_000_000_000 -> '1,5 nghìn tỷ'
    """
    if amount < 0:
        return f"-{format_vnd_general(abs(amount))}"
    
    units = [
        ("đồng", 1),
        ("nghìn", 1_000),
        ("triệu", 1_000_000),
        ("tỷ", 1_000_000_000),
        ("nghìn tỷ", 1_000_000_000_000),
        ("triệu tỷ", 1_000_000_000_000_000),
    ]
    
    for i in range(len(units) - 1, -1, -1):
        name, value = units[i]
        if amount >= value:
            result = amount / value
            result_str = f"{result:.2f}".rstrip('0').rstrip('.')
            return f"{result_str} {name}"
    
    return f"{amount} đồng"
