# Bill/Invoice API - Flow Documentation

## 📋 Overview

API này xử lý việc trích xuất thông tin từ hóa đơn/invoice sử dụng Gemini AI theo flow hoàn chỉnh từ upload, xử lý, lưu trữ đến quản lý job.

## 🚀 Flow Tổng Quan

### 1. Khởi động (Startup)

```
startup_event() → Load config → Khởi tạo GeminiInvoiceExtractor → Sẵn sàng xử lý
```

### 2. Single Extraction Flow

**POST `/api/v1/bills/extract`**

```
1. Client upload file ảnh hóa đơn
   ↓
2. Validate file (định dạng, kích thước)
   ↓
3. Lưu file vào uploads/ với UUID
   ↓
4. Gọi extractor.extract() → Gemini API
   ↓
5. Parse & validate JSON response
   ↓
6. Lưu kết quả vào output/ (nếu save_result=True)
   ↓
7. Trả về response với data + metadata
   ↓
8. Clean up file tạm trong finally block
```

### 3. Batch Extraction Flow

**POST `/api/v1/bills/extract/batch`**

```
1. Client upload nhiều files
   ↓
2. Validate & lưu tất cả files vào uploads/
   ↓
3. Tạo job_id và job record trong jobs_db (in-memory)
   ↓
4. Trả về response ngay với job_id và status_url
   ↓
5. Background task xử lý từng file:
   - Extract → Save result to output/
   - Update job progress
   - Clean up files
   ↓
6. Client theo dõi qua GET /jobs/{job_id}
```

## 📁 Directory Structure

```
vicobi-ai/
├── uploads/        # Temporary uploaded files
├── output/         # Extraction results (JSON)
├── temp/           # ZIP downloads
└── app/
    ├── routers/
    │   └── bill.py # Main API endpoints
    ├── schemas/
    │   └── bill.py # Pydantic models
    ├── models/
    │   └── bill.py # InvoiceData model
    ├── src/
    │   └── gemini_extractor/
    │       ├── config.py
    │       └── pipeline.py
    └── config/
        └── gemini_config.yaml
```

## 🔌 API Endpoints

### Health Check

**GET `/api/v1/bills/`** or **GET `/api/v1/bills/health`**

Response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "extractor_initialized": true,
  "config_loaded": true,
  "model_version": "gemini-2.5-flash"
}
```

### Single Extraction

**POST `/api/v1/bills/extract`**

Request (multipart/form-data):

- `file`: Image file (JPG, PNG, BMP, max 10MB)
- `prompt`: Optional custom prompt (default: "Extract invoice data to JSON")
- `return_raw`: Optional boolean (default: false)
- `save_result`: Optional boolean (default: true)

Response:

```json
{
  "success": true,
  "message": "Extraction completed successfully",
  "data": {
    "SELLER": "Company Name",
    "TIMESTAMP": "2025-11-20 10:00:00",
    "PRODUCTS": [
      {
        "PRODUCT": "Product 1",
        "NUM": 2,
        "VALUE": 100000.0
      }
    ],
    "TOTAL_COST": 100000.0,
    "ADDRESS": "123 Street",
    "TAX_CODE": "0123456789"
  },
  "job_id": "uuid-here",
  "processing_time": 2.5,
  "metadata": {
    "filename": "invoice.jpg",
    "file_size": 1024000,
    "timestamp": "2025-11-20T10:00:00"
  }
}
```

### Batch Extraction

**POST `/api/v1/bills/extract/batch`**

Request (multipart/form-data):

- `files`: Multiple image files
- `prompt`: Optional custom prompt
- `continue_on_error`: Optional boolean (default: true)

Response:

```json
{
  "success": true,
  "message": "Batch processing started",
  "job_id": "uuid-here",
  "total_files": 10,
  "status_url": "/api/v1/bills/jobs/uuid-here"
}
```

### Job Management

**GET `/api/v1/bills/jobs/{job_id}`** - Get job status

Response:

```json
{
  "job_id": "uuid-here",
  "status": "processing",  // or "completed"
  "total_files": 10,
  "processed": 5,
  "success": 4,
  "failed": 1,
  "results": [...],
  "errors": [...],
  "created_at": "2025-11-20T10:00:00",
  "updated_at": "2025-11-20T10:05:00"
}
```

**GET `/api/v1/bills/jobs/{job_id}/results`** - Get detailed results

**GET `/api/v1/bills/jobs/{job_id}/download`** - Download ZIP of all results

**GET `/api/v1/bills/jobs`** - List all jobs

- Query params: `status` (optional), `limit` (default: 100)

**DELETE `/api/v1/bills/jobs/{job_id}`** - Delete job and files

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Config File

Edit `app/config/gemini_config.yaml`:

```yaml
api:
  api_key: ${GEMINI_API_KEY}
  model_version: "gemini-2.5-flash"
  # ... other settings
```

## 📊 Data Models

### InvoiceData

```python
{
  "SELLER": str,           # Seller name
  "TIMESTAMP": str,        # Transaction timestamp
  "PRODUCTS": [            # List of products
    {
      "PRODUCT": str,      # Product name
      "NUM": int,          # Quantity
      "VALUE": float       # Total value
    }
  ],
  "TOTAL_COST": float,     # Total cost
  "ADDRESS": str?,         # Seller address (optional)
  "TAX_CODE": str?         # Tax code (optional)
}
```

## 🧹 Cleanup Strategy

1. **Single extraction**: File xóa ngay sau xử lý (finally block)
2. **Batch extraction**: File xóa sau khi xử lý từng file
3. **Shutdown**: Xóa toàn bộ temp/ directory
4. **Manual**: DELETE `/jobs/{job_id}` xóa output files và ZIP

## 🔄 State Management

- **In-memory**: `jobs_db` dictionary (không persistent, mất khi restart)
- **File system**:
  - `uploads/` - Files tạm từ upload
  - `output/` - Kết quả JSON
  - `temp/` - ZIP downloads

## ⚠️ Error Handling

All endpoints handle errors với:

- Try/catch blocks
- HTTPException với status codes (400, 500, 503)
- Logger warnings/errors
- Finally blocks để cleanup

## 🚀 Running the API

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GEMINI_API_KEY=your_key_here

# Run server
uvicorn app.main:app --reload

# Access docs
open http://localhost:8000/docs
```

## 📝 TODO

- [ ] Implement actual Gemini API integration in `pipeline.py`
- [ ] Add authentication/authorization
- [ ] Add rate limiting
- [ ] Persistent job storage (database)
- [ ] Add retry mechanism for failed extractions
- [ ] Add webhook notifications for batch completion
- [ ] Add file format validation beyond extension check
- [ ] Add virus scanning for uploaded files
