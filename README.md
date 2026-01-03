# Vicobi AI

## Giới thiệu Project

**Vicobi AI** là một hệ thống API backend xử lý dữ liệu đa phương thức (multimodal) sử dụng công nghệ AI tiên tiến. Project tập trung vào hai chức năng chính: **xử lý giọng nói** (voice processing) và **trích xuất thông tin hóa đơn** (bill/invoice extraction) thông qua các mô hình AI và OCR.

### Chủ đề

Hệ thống AI backend phục vụ cho ứng dụng Vicobi, cung cấp khả năng:

- Chuyển đổi giọng nói thành văn bản (Speech-to-Text) bằng PhoWhisper
- Trích xuất và phân tích thông tin từ hóa đơn/biên lai bằng AWS Bedrock AI và OCR
- Xử lý và lưu trữ dữ liệu thông qua MongoDB
- Cung cấp RESTful API với tài liệu tự động (Swagger UI)

### Tính năng chính

#### Xử lý Giọng nói (Voice Processing)

- **Speech Recognition**: Chuyển đổi audio thành text với PhoWhisper model
- **Trích xuất thông tin**: Trích xuất thông tin có cấu trúc từ nội dung giọng nói
- **Hỗ trợ đa ngôn ngữ**: Tiếng Việt và tiếng Anh
- **Hỗ trợ định dạng**: MP3, WAV, M4A, v.v.

#### Xử lý Hóa đơn (Bill/Invoice Processing)

- **OCR Processing**: Nhận dạng ký tự từ ảnh hóa đơn (EasyOCR)
- **Trích xuất bằng AI**: Trích xuất thông tin có cấu trúc (tên cửa hàng, số tiền, ngày tháng, sản phẩm)
- **Phân loại hóa đơn**: Phân loại loại hóa đơn bằng PyTorch model
- **Xử lý ảnh**: Xử lý và tối ưu hóa ảnh trước khi OCR

#### Chatbot RAG (Retrieval-Augmented Generation)

- **Hỏi đáp thông minh**: Trả lời câu hỏi dựa trên context được cung cấp
- **Vector Search**: Tìm kiếm ngữ nghĩa với Qdrant vector database
- **Embedding Model**: Sử dụng multilingual sentence transformers
- **Auto-initialization**: Tự động load context files khi khởi động app
- **File Management**: Upload, delete và quản lý file PDF/TXT
- **Context-aware**: Trả lời chính xác dựa trên tài liệu đã index

#### Xác thực & Bảo mật (Authentication & Security)

- **Tích hợp AWS Cognito**: Xác thực người dùng qua JWT tokens
- **Cấu hình bảo mật**: Quản lý bảo mật với environment variables
- **Cấu hình CORS**: Kiểm soát truy cập cross-origin

#### Quản lý Dữ liệu (Data Management)

- **Tích hợp MongoDB**: Lưu trữ NoSQL với MongoEngine ODM
- **Database Models**: Models cho dữ liệu Voice, Bill và User
- **Xác thực dữ liệu**: Validation với Pydantic schemas

### Công nghệ sử dụng

#### Backend Framework

- **FastAPI** (v0.115.5): Web framework hiện đại, hiệu suất cao cho Python
- **Uvicorn**: ASGI server với hỗ trợ async
- **Python 3.13**: Phiên bản Python mới nhất

#### AI & Machine Learning

- **AWS Bedrock** (Claude 3.5 Sonnet): AI model cho information extraction
- **Transformers** (v4.46.3): Hugging Face library cho NLP models
- **PyTorch** (v2.9.1): Deep learning framework
- **PhoWhisper**: Vietnamese speech recognition model
- **EasyOCR**: OCR engine với Vietnamese support
- **Sentence Transformers**: Multilingual embedding models cho semantic search
- **LangChain**: Framework cho RAG implementation

#### Cơ sở Dữ liệu & Lưu trữ (Database & Storage)

- **MongoDB** (latest): NoSQL document database
- **MongoEngine** (v0.29.1): ODM (Object-Document Mapper)
- **Qdrant**: Vector database cho semantic search và RAG

#### Thư viện Bổ sung (Additional Libraries)

- **Pydantic**: Validation dữ liệu và quản lý cấu hình
- **Loguru**: Hệ thống logging có cấu trúc
- **Pillow & OpenCV**: Xử lý ảnh
- **PyDub & AudioOp**: Xử lý audio
- **boto3**: AWS SDK cho tích hợp Bedrock

---

## Tổng quan Source Code

### Cấu trúc thư mục chi tiết

```
vicobi-ai/
├── app/                                    # Application root
│   ├── __init__.py                        # Package initialization
│   ├── main.py                            # FastAPI app entry point & lifespan management
│   ├── config.py                          # Configuration & environment variables
│   ├── database.py                        # MongoDB connection setup
│   ├── auth.py                            # AWS Cognito authentication
│   │
│   ├── routers/                           # API Endpoints (Controllers)
│   │   ├── __init__.py
│   │   ├── voice.py                       # Voice processing endpoints
│   │   ├── bill.py                        # Bill extraction endpoints
│   │   └── chatbot.py                     # Chatbot RAG endpoints
│   │
│   ├── models/                            # Database Models (MongoEngine)
│   │   ├── __init__.py
│   │   ├── voice.py                       # Voice document model
│   │   ├── bill.py                        # Bill document model
│   │   ├── enum.py                        # Enumerations
│   │   └── README.md
│   │
│   ├── schemas/                           # Pydantic Schemas (Request/Response)
│   │   ├── __init__.py
│   │   ├── base.py                        # Base schemas
│   │   ├── voice.py                       # Voice request/response schemas
│   │   ├── bill.py                        # Bill request/response schemas
│   │   └── README.md
│   │
│   ├── services/                          # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── voice_service.py               # Voice processing business logic
│   │   ├── bill_service.py                # Bill processing business logic
│   │   ├── chatbot_service.py             # Chatbot RAG business logic
│   │   ├── context_initializer.py         # Auto-load context files at startup
│   │   ├── utils.py                       # Utility functions
│   │   │
│   │   └── bedrock_extractor/             # AWS Bedrock AI Integration
│   │       ├── __init__.py
│   │       ├── service.py                 # Main Bedrock service
│   │       ├── config.py                  # Bedrock configuration
│   │       ├── voice.py                   # Voice extraction với Bedrock
│   │       ├── bill.py                    # Bill extraction với Bedrock
│   │       └── chatbot.py                 # Chatbot response generation
│   │
│   ├── ai_models/                         # AI Model Management
│   │   ├── __init__.py
│   │   ├── voice.py                       # PhoWhisper model loader
│   │   ├── bill.py                        # Bill classifier model
│   │   ├── embeddings.py                  # Embedding model for semantic search
│   │   ├── context/                       # Context files for RAG (auto-embedded)
│   │   │   └── *.pdf, *.txt               # Knowledge base documents
│   └── prompts/                           # AI Prompts Templates
│       ├── extraction_voice_en.txt        # Voice extraction prompt (English)
│       ├── extraction_voice_vi.txt        # Voice extraction prompt (Vietnamese)
│       ├── extraction_bill_en.txt         # Bill extraction prompt (English)
│       ├── extraction_bill_vi.txt         # Bill extraction prompt (Vietnamese)
│       └── chat_system_prompt.txt         # Chatbot system prompt with markdown formatting
│       ├── extraction_voice_vi.txt        # Voice extraction prompt (Vietnamese)
│       ├── extraction_bill_en.txt         # Bill extraction prompt (English)
│       └── extraction_bill_vi.txt         # Bill extraction prompt (Vietnamese)
│
├── docker-compose.yml                      # Docker orchestration
├── Dockerfile                              # Container image definition
├── requirements.txt                        # Python dependencies
├── .env                                    # Environment variables (git ignored)
├── .env-example                            # Environment template
└── README.md                               # Documentation
```

### Kiến trúc và luồng xử lý

#### 1. Luồng xử lý Request (Request Flow)

```
Client Request → FastAPI Router → Service Layer → AI Models/Extractors → Database → Response
```

#### 2. Các Layers và Trách nhiệm

**Router Layer** (`app/routers/`)

- Định nghĩa API endpoints
- Validate dữ liệu request với Pydantic schemas
- Kiểm tra xác thực (authentication)
- Gọi service layer
- Format response

**Service Layer** (`app/services/`)

- Logic nghiệp vụ chính
- Điều phối giữa AI models và database
- Xử lý lỗi và retry logic
- Chuyển đổi dữ liệu

**AI Models Layer** (`app/ai_models/`, `app/services/bedrock_extractor/`)

- Load và quản lý AI models
- Nhận dạng giọng nói (PhoWhisper)
- Trích xuất thông tin (AWS Bedrock với Claude 3.5 Sonnet)
- Phân loại hóa đơn (PyTorch)
- Xử lý OCR (EasyOCR)

**Data Layer** (`app/models/`, `app/database.py`)

- Quản lý kết nối database
- MongoEngine document models
- Các thao tác CRUD

#### 3. Các Component Chính

**app/main.py**

- Khởi tạo FastAPI application
- Quản lý vòng đời (startup/shutdown)
- Pre-loading AI models
- Cấu hình CORS middleware
- Đăng ký routes

**app/config.py**

- Quản lý cấu hình tập trung
- Load environment variables
- Định nghĩa giá trị mặc định
- Type-safe settings với Pydantic

**app/auth.py**

- Xác thực AWS Cognito JWT token
- Decorator xác thực người dùng
- Logic validation token

**app/services/bedrock_extractor/**

- Tích hợp AWS Bedrock (Claude 3.5 Sonnet)
- Trích xuất thông tin có cấu trúc từ text/image
- Prompt engineering với custom templates

**app/ai_models/voice.py**

- Singleton loader cho PhoWhisper model
- Pipeline chuyển đổi audio
- Cơ chế caching để tối ưu hiệu suất

---

## Hướng dẫn chạy code trực tiếp

### Yêu cầu hệ thống

- **Python**: 3.10+ (khuyên dùng 3.13)
- **RAM**: Tối thiểu 8GB (khuyên dùng 16GB)
- **Disk Space**: ~5GB cho dependencies và AI models
- **Docker**: Version 20.10+ (nếu chạy bằng Docker)

---

## Phương án 1: Chạy với Virtual Environment

### Bước 1: Clone và Setup Environment

```bash
# Clone repository
git clone https://gitlab.com/vicobi/vicobi-ai.git
cd vicobi-ai

# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip và cài dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

> **Lưu ý**: Quá trình cài đặt mất 10-15 phút do các thư viện AI lớn

### Bước 2: Cấu hình Environment Variables

**Tạo file `.env`:**

```cmd
# Windows
copy .env-example .env

# macOS/Linux
cp .env-example .env
```

**Chỉnh sửa `.env` với thông tin thực tế:**

```env
# Project
PROJECT_NAME=VicobiAI
API_PREFIX=/api/v1/ai
ENVIRONMENT=development

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_INITDB_ROOT_PASSWORD=your_password
MONGO_INITDB_DATABASE=VicobiMongoDB

# AWS Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# AWS Cognito
USER_POOL_ID=your_pool_id
APP_CLIENT_ID=your_client_id
REGION=ap-southeast-1

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=vicobi_knowledge

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### Bước 3: Khởi động MongoDB và Qdrant

```bash
# Chạy MongoDB với Docker
docker run -d \
  --name vicobi-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=mongo \
  -e MONGO_INITDB_ROOT_PASSWORD=your_password \
  -e MONGO_INITDB_DATABASE=VicobiMongoDB \
  -v mongo_data:/data/db \
  mongo:latest

# Chạy Qdrant Vector Database với Docker
docker run -d \
  --name vicobi-qdrant \
  -p 6333:6333 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest
```

### Bước 4: Chạy Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bước 5: Truy cập Application

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Phương án 2: Chạy với Docker Compose

---

### Bước 1: Clone và Cấu hình

```bash
# Clone repository
git clone https://gitlab.com/vicobi/vicobi-ai.git
cd vicobi-ai

# Tạo file .env
# Windows:
copy .env-example .env
# macOS/Linux:
cp .env-example .env
```

**Chỉnh sửa file `.env`** với credentials thực tế (tương tự như Phương án 1)

### Bước 2: Chạy Docker Compose

```bash
# Build và start tất cả services
docker compose up -d
```

Output:

```
[+] Running 3/3
 ✔ Network vicobi-ai_default    Created
 ✔ Container vicobi-mongo       Started
 ✔ Container vicobi-ai-service  Started
```

### Bước 3: Kiểm tra Services

```bash
# Check container status
docker compose ps

# Xem logs
docker compose logs -f
```

### Bước 4: Truy cập Application

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Commands thường dùng

```bash
# Stop services
docker compose stop

# Start services
docker compose start

# Restart services
docker compose restart

# Stop và xóa containers
docker compose down

# Stop và xóa containers + data (cẩn thận)
docker compose down -v

# Rebuild images
docker compose build --no-cache
docker compose up -d

# Xem logs
docker compose logs -f ai-service
docker compose logs -f mongo

# Xem resource usage
docker stats

# Access container shell
docker compose exec ai-service bash
docker compose exec mongo mongosh -u mongo -p your_password
```

### Sao lưu & Khôi phục MongoDB (Backup & Restore)

**Sao lưu:**

```bash
docker compose exec mongo mongodump \
  --username mongo \
  --password your_password \
  --authenticationDatabase admin \
  --out /data/backup
```

**Khôi phục:**

```bash
docker compose exec mongo mongorestore \
  --username mongo \
  --password your_password \
  --authenticationDatabase admin \
  /data/backup
```

---

## Kiểm thử API (Testing)

**Kiểm tra Health Hệ thống:**

```bash
curl http://localhost:8000/health
```

**Kiểm tra Health Voice Service:**

```bash
curl -X GET "http://localhost:8000/api/v1/ai/voices/health" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Xử lý Giọng nói (Voice Processing):**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/voices/process" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.mp3"
```

**Kiểm tra Health Bill Service:**

```bash
curl -X GET "http://localhost:8000/api/v1/ai/bills/health" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Trích xuất Hóa đơn (Bill Extraction):**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/bills/extract" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@bill.jpg"
```

**Kiểm tra Health Chatbot Service:**

```bash
curl -X GET "http://localhost:8000/api/v1/ai/chatbot/health" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

**Hỏi đáp với Chatbot:**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/chatbot/ask" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Phí chuyển khoản là bao nhiêu?"}'
```

**Upload file context:**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/chatbot/ingest" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@knowledge.pdf"
```

**Lấy danh sách files:**

```bash
curl -X GET "http://localhost:8000/api/v1/ai/chatbot/files" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

**Xóa một file:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/ai/chatbot/files/knowledge.pdf" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

---

## Khắc phục Sự cố (Troubleshooting)

### Lỗi: Port đã được sử dụng

```bash
# Windows
netstat -ano | findstr :8000
# macOS/Linux
lsof -i :8000

# Đổi port trong docker-compose.yml hoặc khi chạy uvicorn
uvicorn app.main:app --reload --port 8001
```

### Lỗi: Kết nối MongoDB thất bại

```bash
# Kiểm tra MongoDB đang chạy
docker ps | grep mongo

# Xem logs
docker compose logs mongo

# Test kết nối
docker compose exec mongo mongosh -u mongo -p your_password
```

### Lỗi: Container liên tục restart

```bash
# Xem logs
docker compose logs ai-service --tail 100

# Xem chi tiết container
docker inspect vicobi-ai-service
```

### Lỗi: AI Models load chậm

- Lần đầu tiên download models mất 5-10 phút
- Đảm bảo kết nối internet ổn định
- Models được cache sau lần load đầu

### Lỗi: AWS Bedrock xác thực thất bại

- Kiểm tra credentials trong file `.env`
- Kiểm tra IAM permissions: `AmazonBedrockFullAccess`
- Test: `aws bedrock list-foundation-models --region ap-southeast-1`
- Đảm bảo model ID có sẵn trong region

### Lỗi: Qdrant connection failed

```bash
# Kiểm tra Qdrant đang chạy
docker ps | grep qdrant

# Xem logs
docker logs vicobi-qdrant

# Test kết nối
curl http://localhost:6333/collections
```

### Lỗi: Context files không được auto-embedded

- Kiểm tra file có đúng định dạng (.pdf hoặc .txt)
- Xem logs khi startup: `docker compose logs ai-service | grep "Context"`
- File phải nằm trong folder `app/ai_models/context/`
- Restart app để trigger auto-initialization

---

## Tài liệu API (API Documentation)

Sau khi khởi động server, truy cập Swagger UI để xem đầy đủ tài liệu API và test endpoints:

**http://localhost:8000/docs**

### Các Endpoints Chính

#### Hệ thống (System)

| Method | Endpoint  | Mô tả                             | Xác thực |
| ------ | --------- | --------------------------------- | -------- |
| GET    | `/health` | Kiểm tra health hệ thống tổng thể | Không    |
| GET    | `/`       | Redirect đến API docs             | Không    |
| GET    | `/docs`   | Swagger UI documentation          | Không    |

#### Giọng nói (Voice Processing)

| Method | Endpoint                    | Mô tả                                         | Xác thực |
| ------ | --------------------------- | --------------------------------------------- | -------- |
| GET    | `/api/v1/ai/voices/health`  | Kiểm tra health Voice Service                 | Có       |
| POST   | `/api/v1/ai/voices/process` | Xử lý audio và trích xuất thông tin (Bedrock) | Có       |

#### Hóa đơn (Bill Processing)

| Method | Endpoint                   | Mô tả                                         | Xác thực |
| ------ | -------------------------- | --------------------------------------------- | -------- |
| GET    | `/api/v1/ai/bills/health`  | Kiểm tra health Bill Service                  | Có       |
| POST   | `/api/v1/ai/bills/extract` | Trích xuất thông tin từ ảnh hóa đơn (Bedrock) | Có       |

#### Chatbot RAG

| Method | Endpoint                          | Mô tả                                          | Xác thực      |
| ------ | --------------------------------- | ---------------------------------------------- | ------------- |
| GET    | `/api/v1/ai/chatbot/health`       | Kiểm tra health Chatbot Service                | Admin         |
| POST   | `/api/v1/ai/chatbot/ask`          | Hỏi đáp với chatbot (member & admin)           | Member, Admin |
| GET    | `/api/v1/ai/chatbot/files`        | Lấy danh sách files đã được ingest             | Admin         |
| POST   | `/api/v1/ai/chatbot/ingest`       | Upload và ingest file PDF/TXT vào vector store | Admin         |
| DELETE | `/api/v1/ai/chatbot/files/{name}` | Xóa một file cụ thể khỏi vector store          | Admin         |
| DELETE | `/api/v1/ai/chatbot/reset`        | Xóa toàn bộ dữ liệu trong collection           | Admin         |

> **Lưu ý**:
>
> - Tất cả các endpoint yêu cầu JWT token từ AWS Cognito trong header `Authorization: Bearer <token>`
> - **Member**: User với role `member` hoặc `admin`
> - **Admin**: Chỉ user với role `admin`

---

## Thực hành Bảo mật Tốt nhất (Security Best Practices)

- **KHÔNG BAO GIỜ** commit file `.env` vào Git
- Sử dụng mật khẩu mạnh cho MongoDB
- Thay đổi API keys định kỳ
- Kiểm tra logs thường xuyên để phát hiện bất thường
- Không để lộ dữ liệu nhạy cảm trong logs
- Sử dụng HTTPS trong môi trường production
- Triển khai rate limiting cho public APIs

---

## Giám sát & Logging (Monitoring & Logging)

**Vị trí Logs:**

- Development: Console output
- Docker: `docker compose logs -f`
- Production: Cấu hình external logging service

**Giám sát Health:**

```bash
# Kiểm tra health đơn giản
curl http://localhost:8000/health

# Giám sát chi tiết với watch
watch -n 5 'curl -s http://localhost:8000/health | jq'
```
