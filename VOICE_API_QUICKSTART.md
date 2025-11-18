# 🎤 Voice Transcription API - Quick Start

API tự động chuyển đổi file âm thanh (mp3, aac, mp2, m4a, ogg, flac...) sang .wav và transcribe thành text bằng PhoWhisper.

## ⚡ Quick Start (3 bước)

### 1. Cài đặt FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ffmpeg

# Kiểm tra
ffmpeg -version
```

### 2. Khởi động server

```bash
cd vicobi-ai
uvicorn app.main:app --reload
```

Server sẽ chạy tại: http://localhost:8000

### 3. Test API

```bash
# Cách 1: Sử dụng test script
python test_api_transcribe.py audio.mp3

# Cách 2: Sử dụng curl
curl -X POST "http://localhost:8000/api/v1/voices/transcribe" \
  -F "file=@audio.mp3"
```

## 📡 Endpoints

### 🎯 POST /api/v1/voices/transcribe

Upload file âm thanh và nhận transcription

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/voices/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.mp3"
```

**Response:**

```json
{
  "success": true,
  "transcription": "Xin chào, đây là nội dung của file âm thanh",
  "original_filename": "audio.mp3",
  "file_format": ".mp3",
  "model": "vinai/PhoWhisper-base"
}
```

### 💚 GET /api/v1/voices/health-check

Kiểm tra trạng thái API

```bash
curl http://localhost:8000/api/v1/voices/health-check
```

## 🎯 Sử dụng trong Code

### Python

```python
import requests

# Upload và transcribe
url = "http://localhost:8000/api/v1/voices/transcribe"
files = {"file": open("audio.mp3", "rb")}
response = requests.post(url, files=files)

result = response.json()
print(f"Transcription: {result['transcription']}")
```

### JavaScript

```javascript
const formData = new FormData();
formData.append("file", audioFile);

fetch("http://localhost:8000/api/v1/voices/transcribe", {
  method: "POST",
  body: formData,
})
  .then((res) => res.json())
  .then((data) => console.log(data.transcription));
```

## 📁 Format được hỗ trợ

✅ MP3, AAC, M4A, MP2, OGG, FLAC, WAV, WMA, OPUS

## 🔧 Cấu trúc Project

```
vicobi-ai/
├── app/
│   ├── main.py                 # FastAPI app + router config
│   ├── utils.py                # convert_audio_to_wav()
│   ├── routers/
│   │   └── voice.py           # /transcribe endpoint
│   ├── services/
│   │   └── voice_service.py   # transcribe_audio_file()
│   └── ai-models/
│       └── voice.py           # PhoWhisper model
├── test_api_transcribe.py     # Test script
└── API_VOICE_TRANSCRIPTION.md # Full documentation
```

## 🛠️ Quy trình xử lý

```
Upload File (mp3/aac/...)
    ↓
Validate Format
    ↓
Convert to WAV (16kHz, Mono) ← convert_audio_to_wav()
    ↓
PhoWhisper Model
    ↓
Return Transcription Text
    ↓
Cleanup Temp Files
```

## 🚀 Testing

### Test với file local

```bash
python test_api_transcribe.py my_audio.mp3
```

### Test với nhiều format

```bash
# MP3
python test_api_transcribe.py audio.mp3

# AAC
python test_api_transcribe.py audio.aac

# M4A (iPhone recording)
python test_api_transcribe.py recording.m4a

# WAV
python test_api_transcribe.py audio.wav
```

### Output mẫu

```
============================================================
  🎤 TEST API VOICE TRANSCRIPTION
============================================================

1️⃣  Kiểm tra server...
✅ Server đang hoạt động!

2️⃣  Test transcription API...

📁 File: audio.mp3
📊 Kích thước: 245.67 KB
🔧 Format: .mp3
🌐 API: http://localhost:8000/api/v1/voices/transcribe
------------------------------------------------------------
⏳ Đang upload và xử lý...

✅ THÀNH CÔNG!
------------------------------------------------------------
🎯 Transcription:
   Xin chào, đây là bản ghi âm test...

📝 Chi tiết:
   - Model: vinai/PhoWhisper-base
   - Original file: audio.mp3
   - Format: .mp3
   - Success: True
------------------------------------------------------------

🎉 Test hoàn tất thành công!
```

## 🔍 Troubleshooting

### "ffmpeg not found"

```bash
# Cài đặt FFmpeg
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
```

### "Connection refused"

```bash
# Khởi động server
uvicorn app.main:app --reload
```

### "Model not found"

Server sẽ tự động download model PhoWhisper lần đầu (có thể mất vài phút)

### Upload file lớn timeout

```python
# Tăng timeout trong test script
response = requests.post(endpoint, files=files, timeout=600)  # 10 phút
```

## 📚 Tài liệu đầy đủ

- **API Documentation**: [API_VOICE_TRANSCRIPTION.md](./API_VOICE_TRANSCRIPTION.md)
- **Audio Converter Guide**: [AUDIO_CONVERTER_GUIDE.md](./AUDIO_CONVERTER_GUIDE.md)
- **Interactive Docs**: http://localhost:8000/docs (khi server đang chạy)

## 💡 Tips

1. **GPU Acceleration**: API tự động sử dụng GPU nếu có CUDA
2. **File Size**: Hỗ trợ file lớn (mặc định <100MB, có thể config tăng)
3. **Batch Processing**: Có thể xử lý nhiều file song song
4. **Caching**: Model được cache sau lần load đầu tiên

## 🤝 Support

Nếu gặp vấn đề:

1. Kiểm tra FFmpeg: `ffmpeg -version`
2. Kiểm tra server: `curl http://localhost:8000/api/v1/voices/health-check`
3. Xem logs: Server terminal output
4. Đọc docs: `API_VOICE_TRANSCRIPTION.md`
