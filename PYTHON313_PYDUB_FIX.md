# 🔧 Troubleshooting: Python 3.13 + pydub

## Vấn đề

Khi chạy với Python 3.13+, bạn có thể gặp lỗi:

```
ModuleNotFoundError: No module named 'pyaudioop'
```

hoặc

```
ModuleNotFoundError: No module named 'audioop'
```

## Nguyên nhân

Từ Python 3.13, module `audioop` (built-in) đã bị loại bỏ. Package `pydub` phụ thuộc vào `audioop` nên sẽ gặp lỗi.

## ✅ Giải pháp

Cài đặt `audioop-lts` - package thay thế cho `audioop`:

```bash
pip install audioop-lts
```

## Cài đặt đầy đủ

### 1. Activate virtual environment

```bash
source .venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

Package `audioop-lts` đã được thêm vào `requirements.txt`, nên lệnh trên sẽ tự động cài nó.

### 3. Verify installation

```bash
python -c "from pydub import AudioSegment; print('✓ OK')"
```

Nếu không có lỗi → Thành công!

## Chi tiết về audioop-lts

- **Package**: [audioop-lts](https://pypi.org/project/audioop-lts/)
- **Mục đích**: Drop-in replacement cho deprecated `audioop` module
- **Python version**: Python 3.13+
- **Platform**: macOS, Linux, Windows

## Kiểm tra version Python

```bash
python --version
```

- Python < 3.13: Không cần `audioop-lts`
- Python >= 3.13: Bắt buộc cần `audioop-lts`

## Alternative Solution

Nếu không muốn dùng `audioop-lts`, có thể downgrade Python xuống 3.12:

```bash
# Dùng pyenv
pyenv install 3.12.0
pyenv local 3.12.0

# Tạo lại virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Updated requirements.txt

File `requirements.txt` đã được cập nhật:

```txt
uvicorn
fastapi
python-multipart
pydantic[email]
pydantic-settings
pytest
mongoengine
transformers
pydub
audioop-lts  # Required for pydub in Python 3.13+
torch
sentencepiece
accelerate
```

## Verify API hoạt động

```bash
# Khởi động server
uvicorn app.main:app --reload

# Test trong terminal khác
curl http://localhost:8000/api/v1/voices/health-check
```

Expected output:

```json
{ "status": "healthy" }
```

## Nếu vẫn gặp lỗi

1. **Xóa virtual environment và tạo lại:**

   ```bash
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Upgrade pip:**

   ```bash
   pip install --upgrade pip
   ```

3. **Cài đặt từng package riêng:**

   ```bash
   pip install pydub
   pip install audioop-lts
   ```

4. **Check installed packages:**
   ```bash
   pip list | grep -E 'pydub|audioop'
   ```

Expected:

```
audioop-lts    0.2.2
pydub          0.25.1
```

## Quick Fix Script

Tạo file `fix_pydub.sh`:

```bash
#!/bin/bash
echo "🔧 Fixing pydub for Python 3.13..."

# Activate venv
source .venv/bin/activate

# Install audioop-lts
pip install audioop-lts

# Test
python -c "from pydub import AudioSegment; print('✓ pydub OK')" && \
python -c "from app.utils import convert_audio_to_wav; print('✓ convert_audio_to_wav OK')" && \
python -c "from app.main import app; print('✓ FastAPI app OK')"

echo "🎉 Done!"
```

Chạy:

```bash
chmod +x fix_pydub.sh
./fix_pydub.sh
```

## Tóm tắt

- ✅ Python 3.13 loại bỏ `audioop` module
- ✅ Cài `audioop-lts` để thay thế
- ✅ Đã thêm vào `requirements.txt`
- ✅ Chạy `pip install -r requirements.txt` để cài
- ✅ Test với `python -c "from pydub import AudioSegment"`
