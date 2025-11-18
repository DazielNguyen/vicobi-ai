# API Voice Transcription - Hướng dẫn sử dụng

## Endpoint: POST /api/v1/voices/transcribe

API này nhận file âm thanh bất kỳ (mp3, aac, m4a, mp2, ogg, flac, wav...), tự động chuyển đổi sang .wav, và trả về text transcription.

## Cài đặt FFmpeg (Bắt buộc)

Trước khi sử dụng API, cần cài đặt FFmpeg:

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

Kiểm tra cài đặt:

```bash
ffmpeg -version
```

## Request

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/voices/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/audio.mp3"
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/v1/voices/transcribe"
files = {"file": open("audio.mp3", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

### Python (httpx - async)

```python
import httpx

async def transcribe_audio(file_path: str):
    url = "http://localhost:8000/api/v1/voices/transcribe"

    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = await client.post(url, files=files)
            return response.json()

# Sử dụng
result = await transcribe_audio("audio.mp3")
print(result)
```

### JavaScript (Fetch API)

```javascript
const formData = new FormData();
formData.append("file", audioFile);

fetch("http://localhost:8000/api/v1/voices/transcribe", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data))
  .catch((error) => console.error("Error:", error));
```

### JavaScript (Axios)

```javascript
const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");

const formData = new FormData();
formData.append("file", fs.createReadStream("audio.mp3"));

axios
  .post("http://localhost:8000/api/v1/voices/transcribe", formData, {
    headers: formData.getHeaders(),
  })
  .then((response) => console.log(response.data))
  .catch((error) => console.error("Error:", error));
```

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "transcription": "Xin chào, đây là nội dung transcription từ file âm thanh",
  "original_filename": "audio.mp3",
  "file_format": ".mp3",
  "model": "vinai/PhoWhisper-base"
}
```

### Error Responses

**400 Bad Request - Tên file không hợp lệ:**

```json
{
  "detail": "Tên file không hợp lệ"
}
```

**400 Bad Request - Format không được hỗ trợ:**

```json
{
  "detail": "File format không được hỗ trợ. Các format được chấp nhận: .mp3, .aac, .m4a, .mp2, .ogg, .flac, .wav, .wma, .opus"
}
```

**404 Not Found - File không tồn tại:**

```json
{
  "detail": "File không tồn tại: /path/to/file"
}
```

**500 Internal Server Error:**

```json
{
  "detail": "Lỗi xử lý file âm thanh: [error message]"
}
```

## Định dạng file được hỗ trợ

- ✅ MP3 (.mp3)
- ✅ AAC (.aac, .m4a)
- ✅ MP2 (.mp2)
- ✅ OGG Vorbis (.ogg)
- ✅ FLAC (.flac)
- ✅ WAV (.wav)
- ✅ WMA (.wma)
- ✅ Opus (.opus)

## Quy trình xử lý

1. **Upload**: Client upload file âm thanh qua multipart/form-data
2. **Validation**: Server validate tên file và format
3. **Save**: Lưu file tạm vào temp directory
4. **Convert**: Chuyển đổi file sang .wav với:
   - Sample rate: 16kHz (tối ưu cho speech recognition)
   - Channels: 1 (Mono)
5. **Transcribe**: Chạy PhoWhisper model để chuyển audio → text
6. **Cleanup**: Xóa các file tạm
7. **Response**: Trả về transcription text + metadata

## Giới hạn và Lưu ý

### Giới hạn kích thước file

Mặc định FastAPI giới hạn upload 100MB. Để tăng:

```python
# Trong main.py
from fastapi import FastAPI

app = FastAPI()
app.router.max_body_size = 500 * 1024 * 1024  # 500 MB
```

### Thời gian xử lý

- File nhỏ (<1 phút): ~2-5 giây
- File trung bình (1-5 phút): ~10-30 giây
- File lớn (>5 phút): Có thể timeout

Để tăng timeout:

```python
import httpx

async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minutes
    response = await client.post(url, files=files)
```

### Model và Ngôn ngữ

- Model: **vinai/PhoWhisper-base**
- Ngôn ngữ: **Tiếng Việt** (Vietnamese)
- Device: CUDA (GPU) nếu có, fallback về CPU

## Testing

### Test với file mẫu

```bash
# Download sample audio
wget https://example.com/sample.mp3 -O test_audio.mp3

# Test API
curl -X POST "http://localhost:8000/api/v1/voices/transcribe" \
  -F "file=@test_audio.mp3"
```

### Test nhiều file

```python
import os
import requests

audio_files = ["audio1.mp3", "audio2.aac", "audio3.wav"]
url = "http://localhost:8000/api/v1/voices/transcribe"

for audio_file in audio_files:
    if os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)

            if response.status_code == 200:
                result = response.json()
                print(f"✓ {audio_file}: {result['transcription'][:50]}...")
            else:
                print(f"✗ {audio_file}: {response.json()['detail']}")
```

## Troubleshooting

### Lỗi: "ffmpeg not found"

→ Cài đặt FFmpeg theo hướng dẫn ở phần đầu

### Lỗi: "Model transcriber chưa được cấu hình"

→ Kiểm tra file `app/ai-models/voice.py` và đảm bảo model đã được load

### Lỗi: "CUDA out of memory"

→ Model đang dùng GPU nhưng hết VRAM. Chuyển về CPU:

```python
# Trong app/ai-models/voice.py
transcriber = pipeline("automatic-speech-recognition",
                       model="vinai/PhoWhisper-base",
                       device="cpu")  # Thay "cuda" → "cpu"
```

### Upload file lớn bị timeout

→ Tăng timeout ở client và server

### Transcription không chính xác

→ Kiểm tra:

- Chất lượng audio gốc
- Có nhiều noise không?
- Ngôn ngữ có phải tiếng Việt không?
- Sample rate có phù hợp không?

## Performance Tips

1. **Giảm kích thước file trước khi upload** (nếu có thể)
2. **Sử dụng GPU** để tăng tốc transcription
3. **Batch processing**: Xử lý nhiều file song song
4. **Caching**: Cache transcription nếu file không đổi
5. **Async processing**: Với file lớn, dùng background task

## Health Check

Kiểm tra API hoạt động:

```bash
curl http://localhost:8000/api/v1/voices/health-check
```

Response:

```json
{
  "status": "healthy"
}
```
