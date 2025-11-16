# Thay đổi API Transcription

## Ngày: 17/11/2025

### Tóm tắt thay đổi

Đã rút gọn và tối ưu hóa API transcription bằng cách:

1. **Chỉ sử dụng PhoWhisper model** - Loại bỏ OpenAI Whisper
2. **Thêm tracking thời gian xử lý** cho từng file và tổng thể

---

## Chi tiết thay đổi

### 1. Loại bỏ OpenAI Whisper

**Lý do:**

- Chỉ xử lý tiếng Việt
- PhoWhisper được tối ưu cho tiếng Việt
- Giảm dependencies và memory footprint

**Thay đổi:**

- ❌ Xóa `import whisper`
- ❌ Xóa function `transcribe_with_openai_whisper()`
- ❌ Xóa endpoint `/api/whisper/openai`
- ❌ Xóa `openai-whisper` khỏi `requirements.txt`

### 2. Đơn giản hóa API

**Endpoint mới:**

```
POST /api/whisper/transcribe
```

**Thay vì:**

- ~~POST /api/whisper/openai~~
- ~~POST /api/whisper/phowhisper~~

### 3. Thêm tracking thời gian xử lý

**Thông tin thời gian trả về:**

```json
{
  "results": [
    {
      "filename": "audio.wav",
      "transcript": "xin chào",
      "model": "vinai/PhoWhisper-small",
      "language": "vi",
      "processing_time_seconds": 2.345,
      "transcription_time_seconds": 1.89
    }
  ],
  "total_files": 1,
  "total_processing_time_seconds": 2.35
}
```

**Giải thích các metrics:**

- `processing_time_seconds`: Thời gian toàn bộ (upload + transcribe + cleanup)
- `transcription_time_seconds`: Chỉ thời gian model transcribe
- `total_processing_time_seconds`: Tổng thời gian xử lý tất cả files

---

## Cách sử dụng mới

### Ví dụ với cURL:

```bash
curl -X POST "http://localhost:8000/api/whisper/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@audio1.wav" \
  -F "files=@audio2.wav" \
  -F "chunk_length_s=30" \
  -F "batch_size=8"
```

### Ví dụ với Python:

```python
import requests

url = "http://localhost:8000/api/whisper/transcribe"
files = [
    ("files", open("audio1.wav", "rb")),
    ("files", open("audio2.wav", "rb"))
]
params = {
    "chunk_length_s": 30,
    "batch_size": 8
}

response = requests.post(url, files=files, params=params)
data = response.json()

for result in data["results"]:
    print(f"File: {result['filename']}")
    print(f"Transcript: {result['transcript']}")
    print(f"Processing time: {result['processing_time_seconds']}s")
    print(f"Transcription time: {result['transcription_time_seconds']}s")
    print("---")

print(f"Total time: {data['total_processing_time_seconds']}s")
```

---

## Performance Tips

1. **Tăng batch_size** (mặc định: 8) để xử lý nhanh hơn (cần nhiều GPU memory)
2. **Điều chỉnh chunk_length_s** (mặc định: 30) tùy độ dài audio
3. API tự động sử dụng GPU nếu có sẵn

---

## Migration Guide

Nếu đang sử dụng endpoint cũ:

### Trước đây:

```python
# OpenAI Whisper
response = requests.post(
    "http://localhost:8000/api/whisper/openai",
    files=[("files", open("audio.wav", "rb"))],
    params={"language": "vi"}
)

# PhoWhisper
response = requests.post(
    "http://localhost:8000/api/whisper/phowhisper",
    files=[("files", open("audio.wav", "rb"))]
)
```

### Bây giờ:

```python
# Chỉ một endpoint duy nhất
response = requests.post(
    "http://localhost:8000/api/whisper/transcribe",
    files=[("files", open("audio.wav", "rb"))]
)
```

---

## Breaking Changes

⚠️ **Các endpoint sau đã bị xóa:**

- `POST /api/whisper/openai`
- `POST /api/whisper/phowhisper`

✅ **Endpoint mới:**

- `POST /api/whisper/transcribe` (PhoWhisper - Vietnamese only)
