# Quick Start Guide - Bill/Invoice API

## ✅ Cấu hình đã hoàn tất

### 📁 Cấu trúc Source Code

```
app/
├── src/
│   └── gemini_extractor/
│       ├── __init__.py         ✅ Module initialization
│       ├── config.py            ✅ Config management với env vars
│       ├── pipeline.py          ✅ Main extractor + BatchProcessor
│       ├── gemini_client.py     ✅ Gemini API client với retry logic
│       ├── preprocessor.py      ✅ Image preprocessing
│       ├── validator.py         ✅ Data validation & normalization
│       └── formatter.py         ✅ Table formatting
├── config/
│   └── gemini_config.yaml       ✅ Configuration file
├── prompts/
│   └── extraction_vi.txt        ✅ Vietnamese extraction prompt
├── routers/
│   └── bill.py                  ✅ API endpoints
└── main.py                      ✅ FastAPI app initialization
```

## 🚀 Chạy API

### 1. Set Environment Variable

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### 2. Start Server (đã chạy)

```bash
uvicorn app.main:app --reload
```

Server đang chạy tại: http://localhost:8000

## 📖 API Documentation

Truy cập: http://localhost:8000/docs

## 🧪 Test API với cURL

### Health Check

```bash
curl http://localhost:8000/api/v1/bills/health
```

### Single Invoice Extraction

```bash
curl -X POST "http://localhost:8000/api/v1/bills/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/invoice.jpg" \
  -F "prompt=Extract invoice data to JSON" \
  -F "save_result=true"
```

### Batch Invoice Extraction

```bash
curl -X POST "http://localhost:8000/api/v1/bills/extract/batch" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/invoice1.jpg" \
  -F "files=@/path/to/invoice2.jpg" \
  -F "files=@/path/to/invoice3.jpg" \
  -F "continue_on_error=true"
```

Response:

```json
{
  "success": true,
  "message": "Batch processing started",
  "job_id": "uuid-here",
  "total_files": 3,
  "status_url": "/api/v1/bills/jobs/uuid-here"
}
```

### Check Job Status

```bash
curl http://localhost:8000/api/v1/bills/jobs/{job_id}
```

### Get Job Results

```bash
curl http://localhost:8000/api/v1/bills/jobs/{job_id}/results
```

### Download Results as ZIP

```bash
curl -O http://localhost:8000/api/v1/bills/jobs/{job_id}/download
```

### List All Jobs

```bash
curl http://localhost:8000/api/v1/bills/jobs?status=completed&limit=10
```

### Delete Job

```bash
curl -X DELETE http://localhost:8000/api/v1/bills/jobs/{job_id}
```

## 🔧 Components Overview

### 1. **GeminiInvoiceExtractor** (pipeline.py)

- Orchestrates the entire extraction process
- Steps:
  1. Image preprocessing (resize, validate)
  2. Call Gemini API with prompt
  3. Parse JSON response
  4. Validate & normalize data
  5. Return structured result

### 2. **GeminiClient** (gemini_client.py)

- Manages Gemini API authentication
- Implements retry logic with exponential backoff
- Handles rate limits automatically
- System prompt integration

### 3. **ImageProcessor** (preprocessor.py)

- Validates image format and size
- Resizes images if too large
- Converts to RGB for Gemini

### 4. **DataValidator** (validator.py)

- Validates JSON structure
- Ensures correct data types
- Cross-checks product totals
- Parses Vietnamese number formats

### 5. **DataNormalizer** (validator.py)

- Normalizes currency values
- Parses Vietnamese date/time formats
- Cleans and standardizes data

### 6. **Config** (config.py)

- Loads YAML configuration
- Resolves environment variables (${VAR_NAME})
- Provides dot-notation access (config.get('api.model_version'))

## 📊 Data Flow

```
Upload Image → Validate → Preprocess → Gemini API → Parse JSON
    ↓
Validate Structure → Normalize Data → Save Result → Return Response
```

## 🎯 Configuration (gemini_config.yaml)

```yaml
api:
  api_key: ${GEMINI_API_KEY} # From env var
  model_version: "gemini-2.5-flash"
  generation:
    temperature: 0.1 # Low for consistency
    top_p: 0.95
    max_output_tokens: 2048
  retry:
    max_retries: 3
    base_delay: 1.0 # Exponential backoff

prompts:
  system_prompt_path: "prompts/extraction_vi.txt"
  language: "vi"

preprocessing:
  max_image_size: 4096 # Resize if larger
  max_file_size_mb: 10

validation:
  strict_mode: true # Raise error on validation failure
  validate_total: true # Check product sum vs total

normalization:
  auto_normalize: true # Auto clean data
```

## 📝 Response Format

```json
{
  "success": true,
  "message": "Extraction completed successfully",
  "data": {
    "SELLER": "Công ty ABC",
    "TIMESTAMP": "20/11/2025 10:30",
    "PRODUCTS": [
      {
        "PRODUCT": "Sản phẩm A",
        "NUM": 2,
        "VALUE": 100000.0
      }
    ],
    "TOTAL_COST": 200000.0,
    "ADDRESS": "123 Đường XYZ",
    "TAX_CODE": "0123456789"
  },
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_time": 2.5,
  "metadata": {
    "filename": "invoice.jpg",
    "file_size": 1024000,
    "timestamp": "2025-11-20T10:00:00"
  }
}
```

## ⚙️ Features

✅ **Single & Batch Processing**: Xử lý 1 hoặc nhiều hóa đơn  
✅ **Async Background Tasks**: Batch không block response  
✅ **Job Management**: Track, list, delete jobs  
✅ **Auto Retry**: Xử lý rate limits tự động  
✅ **Data Validation**: Đảm bảo dữ liệu chính xác  
✅ **Vietnamese Support**: Xử lý tiếng Việt có dấu  
✅ **Flexible Config**: YAML + env variables  
✅ **Error Handling**: Comprehensive try/catch  
✅ **File Cleanup**: Tự động xóa file tạm

## 🔍 Troubleshooting

### Lỗi: "Extractor not initialized"

- Kiểm tra `GEMINI_API_KEY` đã set chưa
- Xem logs khi startup: `uvicorn app.main:app --reload`

### Lỗi: "Invalid JSON in response"

- Gemini trả về không đúng format
- Check prompt trong `prompts/extraction_vi.txt`
- Có thể cần điều chỉnh `temperature` trong config

### Lỗi: "Rate limit exceeded"

- GeminiClient tự động retry
- Nếu vẫn lỗi, tăng `max_delay` trong config

## 📚 Next Steps

1. Test với hóa đơn thật
2. Điều chỉnh prompt nếu cần
3. Thêm authentication (nếu cần)
4. Setup persistent job storage (database)
5. Add webhook notifications cho batch jobs

## 🎉 Hoàn tất!

API đã sẵn sàng xử lý hóa đơn với Gemini AI!
