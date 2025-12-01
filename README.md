# 🚀 Vicobi AI

## 📖 Giới thiệu Project

**Vicobi AI** là một hệ thống API backend xử lý dữ liệu đa phương thức (multimodal) sử dụng công nghệ AI tiên tiến. Project tập trung vào hai chức năng chính: **xử lý giọng nói** (voice processing) và **trích xuất thông tin hóa đơn** (bill/invoice extraction) thông qua các mô hình AI và OCR.

### 🎯 Chủ đề

Hệ thống AI backend phục vụ cho ứng dụng Vicobi, cung cấp khả năng:

- Chuyển đổi giọng nói thành văn bản (Speech-to-Text) bằng PhoWhisper
- Trích xuất và phân tích thông tin từ hóa đơn/biên lai bằng AWS Bedrock AI và OCR
- Xử lý và lưu trữ dữ liệu thông qua MongoDB
- Cung cấp RESTful API với tài liệu tự động (Swagger UI)

### ✨ Tính năng chính

#### 🎤 Voice Processing

- **Speech Recognition**: Chuyển đổi audio thành text với PhoWhisper model
- **Voice Information Extraction**: Trích xuất thông tin có cấu trúc từ nội dung giọng nói
- **Multi-language Support**: Hỗ trợ tiếng Việt và tiếng Anh
- **Format Support**: Hỗ trợ nhiều định dạng audio (MP3, WAV, M4A, etc.)

#### 📄 Bill/Invoice Processing

- **OCR Processing**: Nhận dạng ký tự từ ảnh hóa đơn (EasyOCR)
- **AI Extraction**: Trích xuất thông tin có cấu trúc (tên cửa hàng, số tiền, ngày tháng, items)
- **Bill Classification**: Phân loại loại hóa đơn bằng PyTorch model
- **Image Processing**: Xử lý và tối ưu hóa ảnh trước khi OCR

#### 🔐 Authentication & Security

- **AWS Cognito Integration**: Xác thực người dùng qua JWT tokens
- **Secure Configuration**: Quản lý bảo mật với environment variables
- **CORS Configuration**: Kiểm soát truy cập cross-origin

#### 🗄️ Data Management

- **MongoDB Integration**: Lưu trữ NoSQL với MongoEngine ODM
- **Database Models**: Models cho Voice, Bill, và User data
- **Data Validation**: Validation với Pydantic schemas

### 🛠️ Công nghệ sử dụng

#### Backend Framework

- **FastAPI** (v0.115.5): Modern, high-performance web framework cho Python
- **Uvicorn**: ASGI server với async support
- **Python 3.13**: Latest Python runtime

#### AI & Machine Learning

- **AWS Bedrock** (Claude 3.5 Sonnet): AI model cho information extraction
- **Transformers** (v4.46.3): Hugging Face library cho NLP models
- **PyTorch** (v2.9.1): Deep learning framework
- **PhoWhisper**: Vietnamese speech recognition model
- **EasyOCR**: OCR engine với Vietnamese support

#### Database & Storage

- **MongoDB** (latest): NoSQL document database
- **MongoEngine** (v0.29.1): ODM (Object-Document Mapper)

#### Additional Libraries

- **Pydantic**: Data validation và settings management
- **Loguru**: Structured logging system
- **Pillow & OpenCV**: Image processing
- **PyDub & AudioOp**: Audio processing
- **boto3**: AWS SDK cho Bedrock integration

---

## 📁 Tổng quan Source Code

### Cấu trúc thư mục chi tiết

```
vicobi-ai/
├── app/                                    # Application root
│   ├── __init__.py                        # Package initialization
│   ├── main.py                            # 🚀 FastAPI app entry point & lifespan management
│   ├── config.py                          # ⚙️ Configuration & environment variables
│   ├── database.py                        # 🗄️ MongoDB connection setup
│   ├── auth.py                            # 🔐 AWS Cognito authentication
│   │
│   ├── routers/                           # 🌐 API Endpoints (Controllers)
│   │   ├── __init__.py
│   │   ├── voice.py                       # Voice processing endpoints
│   │   └── bill.py                        # Bill extraction endpoints
│   │
│   ├── models/                            # 💾 Database Models (MongoEngine)
│   │   ├── __init__.py
│   │   ├── voice.py                       # Voice document model
│   │   ├── bill.py                        # Bill document model
│   │   ├── enum.py                        # Enumerations
│   │   └── README.md
│   │
│   ├── schemas/                           # 📋 Pydantic Schemas (Request/Response)
│   │   ├── __init__.py
│   │   ├── base.py                        # Base schemas
│   │   ├── voice.py                       # Voice request/response schemas
│   │   ├── bill.py                        # Bill request/response schemas
│   │   └── README.md
│   │
│   ├── services/                          # 💼 Business Logic Layer
│   │   ├── __init__.py
│   │   ├── voice_service.py               # Voice processing business logic
│   │   ├── bill_service.py                # Bill processing business logic
│   │   ├── utils.py                       # Utility functions
│   │   │
│   │   └── bedrock_extractor/             # 🤖 AWS Bedrock AI Integration
│   │       ├── __init__.py
│   │       ├── service.py                 # Main Bedrock service
│   │       ├── config.py                  # Bedrock configuration
│   │       ├── voice.py                   # Voice extraction với Bedrock
│   │       └── bill.py                    # Bill extraction với Bedrock
│   │
│   ├── ai_models/                         # 🎓 AI Model Management
│   │   ├── __init__.py
│   │   ├── voice.py                       # PhoWhisper model loader
│   │   ├── bill.py                        # Bill classifier model
│   │   └── saved_models/                  # Pre-trained models
│   │       └── pytorch-bill_classifier.pth
│   │
│   └── prompts/                           # 📝 AI Prompts Templates
│       ├── extraction_voice_en.txt        # Voice extraction prompt (English)
│       ├── extraction_voice_vi.txt        # Voice extraction prompt (Vietnamese)
│       ├── extraction_bill_en.txt         # Bill extraction prompt (English)
│       └── extraction_bill_vi.txt         # Bill extraction prompt (Vietnamese)
│
├── docker-compose.yml                      # 🐳 Docker orchestration
├── Dockerfile                              # 🐳 Container image definition
├── requirements.txt                        # 📦 Python dependencies
├── .env                                    # 🔒 Environment variables (git ignored)
├── .env-example                            # 📄 Environment template
└── README.md                               # 📖 Documentation
```

### Kiến trúc và luồng xử lý

#### 1. Request Flow

```
Client Request → FastAPI Router → Service Layer → AI Models/Extractors → Database → Response
```

#### 2. Layers và Responsibilities

**Router Layer** (`app/routers/`)

- Định nghĩa API endpoints
- Validate request data với Pydantic schemas
- Authentication check
- Call service layer
- Format response

**Service Layer** (`app/services/`)

- Business logic chính
- Orchestrate giữa AI models và database
- Error handling và retry logic
- Data transformation

**AI Models Layer** (`app/ai_models/`, `app/services/bedrock_extractor/`)

- Load và manage AI models
- Speech recognition (PhoWhisper)
- Information extraction (AWS Bedrock with Claude 3.5 Sonnet)
- Bill classification (PyTorch)
- OCR processing (EasyOCR)

**Data Layer** (`app/models/`, `app/database.py`)

- Database connection management
- MongoEngine document models
- CRUD operations

#### 3. Key Components

**app/main.py**

- FastAPI application initialization
- Lifespan management (startup/shutdown)
- AI models pre-loading
- CORS middleware configuration
- Routes registration

**app/config.py**

- Centralized configuration management
- Environment variables loading
- Default values definition
- Type-safe settings với Pydantic

**app/auth.py**

- AWS Cognito JWT token verification
- User authentication decorator
- Token validation logic

**app/services/bedrock_extractor/**

- AWS Bedrock (Claude 3.5 Sonnet) integration
- Structured information extraction từ text/image
- Prompt engineering với custom templates

**app/ai_models/voice.py**

- PhoWhisper model singleton loader
- Audio transcription pipeline
- Caching mechanism cho performance

---

## 🚀 Hướng dẫn chạy code trực tiếp

### Yêu cầu hệ thống

- **Python**: 3.10 hoặc cao hơn (khuyên dùng 3.13)
- **RAM**: Tối thiểu 8GB (khuyên dùng 16GB vì AI models)
- **Disk Space**: ~5GB cho dependencies và models
- **MongoDB**: Local installation hoặc Docker
- **OS**: Windows, macOS, hoặc Linux

### Bước 1: Clone repository

```bash
git clone https://gitlab.com/vicobi/vicobi-ai.git
cd vicobi-ai
```

### Bước 2: Tạo Python Virtual Environment

**Windows:**

```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> ⏱️ **Lưu ý**: Quá trình cài đặt có thể mất 10-15 phút do các thư viện AI lớn (PyTorch, Transformers, etc.)

### Bước 4: Cấu hình Environment Variables

1. **Tạo file `.env`** từ template:

**Windows:**

```cmd
copy .env-example .env
```

**macOS/Linux:**

```bash
cp .env-example .env
```

2. **Chỉnh sửa file `.env`** với các giá trị thực tế:

````env
# === Project Configuration ===
PROJECT_NAME=VicobiAI
API_PREFIX=/api/v1/ai
VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True

# === MongoDB Configuration ===
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_INITDB_ROOT_PASSWORD=your_secure_password_here
MONGO_INITDB_DATABASE=VicobiMongoDB

# === AWS Bedrock AI ===
AWS_REGION=ap-southeast-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
BEDROCK_TIMEOUT=60
BEDROCK_TEMPERATURE=0.0
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# === AWS Cognito Authentication ===
USER_POOL_ID=your_cognito_user_pool_id
APP_CLIENT_ID=your_cognito_app_client_id
REGION=ap-southeast-1

# === CORS Configuration ===
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

> 🔑 **Quan trọng**:
>
> - **Bắt buộc có AWS credentials** để sử dụng Bedrock AI
> - Đảm bảo AWS IAM user có quyền truy cập Bedrock service
> - MongoDB credentials phải match với MongoDB instance của bạn

### Bước 5: Khởi động MongoDB

**Option 1: Sử dụng Docker (Khuyên dùng)**

```bash
docker run -d \
  --name vicobi-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=mongo \
  -e MONGO_INITDB_ROOT_PASSWORD=your_secure_password_here \
  -e MONGO_INITDB_DATABASE=VicobiMongoDB \
  -v mongo_data:/data/db \
  mongo:latest
````

**Option 2: MongoDB Local Installation**

**Windows:**

- Download MongoDB Community Server từ [mongodb.com](https://www.mongodb.com/try/download/community)
- Install và chạy MongoDB service
- MongoDB sẽ chạy tại `mongodb://localhost:27017`

**macOS:**

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Bước 6: Chạy Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Parameters:**

- `--reload`: Auto-reload khi code thay đổi (chỉ dùng development)
- `--host 0.0.0.0`: Cho phép truy cập từ mọi network interface
- `--port 8000`: Port của API server

### Bước 7: Verify Application

Sau khi khởi động thành công, bạn sẽ thấy logs:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
--- ⏳ Đang tải PhoWhisper Model... ---
--- ✅ PhoWhisper Model đã sẵn sàng! ---
✅ STARTUP: Toàn bộ AI Service & Model đã sẵn sàng nhận request!
```

**Truy cập các URLs:**

- **API Server**: http://localhost:8000
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Testing API

**Health Check:**

```bash
curl http://localhost:8000/health
```

**Test Voice Transcription:**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/voice/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_audio_file.mp3" \
  -F "language=vi"
```

**Test Bill Extraction:**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/bill/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_bill_image.jpg" \
  -F "language=vi"
```

### Troubleshooting

**Problem: Port 8000 already in use**

```bash
# Đổi sang port khác
uvicorn app.main:app --reload --port 8001
```

**Problem: MongoDB connection failed**

- Kiểm tra MongoDB đã chạy: `docker ps` hoặc `systemctl status mongodb`
- Verify credentials trong `.env` file
- Check MongoDB logs: `docker logs vicobi-mongo`

**Problem: AI Models loading too slow**

- Models sẽ tự động download lần đầu tiên (có thể mất 5-10 phút)
- Đảm bảo có kết nối internet tốt
- Models được cache sau lần load đầu

**Problem: AWS Bedrock authentication failed**

- Verify AWS credentials trong `.env`
- Check AWS IAM permissions cho Bedrock (cần policy `AmazonBedrockFullAccess`)
- Đảm bảo model ID đúng và available trong region của bạn
- Test AWS credentials: `aws bedrock list-foundation-models --region ap-southeast-1`

---

## 🐳 Hướng dẫn chạy Docker

Docker setup đơn giản hóa deployment bằng cách đóng gói toàn bộ application và dependencies vào containers.

### Yêu cầu

- **Docker**: Version 20.10 hoặc cao hơn
- **Docker Compose**: Version 2.0 hoặc cao hơn
- **Disk Space**: ~8GB cho images và volumes

### Cài đặt Docker

**Windows:**

- Download và cài [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Khởi động Docker Desktop

**macOS:**

- Download và cài [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
- Hoặc dùng Homebrew: `brew install --cask docker`

**Linux (Ubuntu/Debian):**

```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Bước 1: Cấu hình Environment

1. **Tạo file `.env`**:

**Windows:**

```cmd
copy .env-example .env
```

**macOS/Linux:**

```bash
cp .env-example .env
```

2. **Update file `.env`** với các credentials thực tế (xem phần "Hướng dẫn chạy code trực tiếp" phía trên)

### Bước 2: Build và Run với Docker Compose

**Start toàn bộ services (AI Service + MongoDB):**

```bash
docker compose up -d
```

**Parameters:**

- `-d`: Detached mode (chạy background)
- Nếu muốn xem logs realtime, bỏ `-d`

**Logs output:**

```
[+] Running 3/3
 ✔ Network vicobi-ai_default       Created
 ✔ Container vicobi-mongo          Started
 ✔ Container vicobi-ai-service     Started
```

### Bước 3: Verify Containers

**Check running containers:**

```bash
docker compose ps
```

Expected output:

```
NAME                   IMAGE              STATUS              PORTS
vicobi-ai-service      vicobi-ai:latest   Up (healthy)        0.0.0.0:8000->8000/tcp
vicobi-mongo           mongo:latest       Up (healthy)        0.0.0.0:27017->27017/tcp
```

**View logs:**

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f ai-service
docker compose logs -f mongo
```

### Bước 4: Access Application

- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **MongoDB**: mongodb://localhost:27017

### Docker Commands Cheat Sheet

**Stop services:**

```bash
docker compose stop
```

**Start services (without rebuilding):**

```bash
docker compose start
```

**Restart services:**

```bash
docker compose restart
```

**Stop và remove containers:**

```bash
docker compose down
```

**Stop và remove containers + volumes (⚠️ xóa data):**

```bash
docker compose down -v
```

**Rebuild images:**

```bash
docker compose build --no-cache
docker compose up -d
```

**View resource usage:**

```bash
docker stats
```

**Execute command trong container:**

```bash
# Access bash shell
docker compose exec ai-service bash

# Run Python command
docker compose exec ai-service python -c "print('Hello')"

# Access MongoDB shell
docker compose exec mongo mongosh -u mongo -p your_password
```

**View container details:**

```bash
docker compose logs ai-service --tail 100
docker inspect vicobi-ai-service
```

### Dockerfile Overview

```dockerfile
FROM python:3.13-slim          # Base image với Python 3.13

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y ffmpeg && \
    apt-get clean

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Services

**ai-service:**

- Build từ Dockerfile local
- Expose port 8000
- Depends on MongoDB
- Auto-restart on failure
- Health check mỗi 90s

**mongo:**

- Official MongoDB image
- Data persistence với named volume
- Authentication enabled
- Health check via mongosh

### Volumes và Data Persistence

**List volumes:**

```bash
docker volume ls
```

**Backup MongoDB data:**

```bash
docker compose exec mongo mongodump \
  --username mongo \
  --password your_password \
  --authenticationDatabase admin \
  --out /data/backup
```

**Restore MongoDB data:**

```bash
docker compose exec mongo mongorestore \
  --username mongo \
  --password your_password \
  --authenticationDatabase admin \
  /data/backup
```

### Troubleshooting Docker

**Problem: Port already in use**

```bash
# Find process using port
# Windows
netstat -ano | findstr :8000
# macOS/Linux
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # host:container
```

**Problem: Container keeps restarting**

```bash
# Check logs
docker compose logs ai-service --tail 50

# Check container status
docker compose ps
docker inspect vicobi-ai-service
```

**Problem: Out of disk space**

```bash
# Remove unused images/containers
docker system prune -a

# Remove specific volumes
docker volume rm vicobi-ai_mongo_data
```

**Problem: Build fails**

```bash
# Clean build without cache
docker compose build --no-cache --pull

# Check Docker daemon
docker info
```

**Problem: MongoDB connection issues**

```bash
# Test MongoDB connection
docker compose exec mongo mongosh \
  mongodb://mongo:your_password@localhost:27017/VicobiMongoDB

# Check MongoDB logs
docker compose logs mongo
```

### Production Deployment Tips

1. **Use production-grade configurations**:

   - Set `ENVIRONMENT=production` trong `.env`
   - Set `DEBUG=False`
   - Use strong passwords
   - Enable SSL/TLS

2. **Resource limits** (thêm vào docker-compose.yml):

```yaml
services:
  ai-service:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 4G
        reservations:
          cpus: "1"
          memory: 2G
```

3. **Logging configuration**:

```yaml
services:
  ai-service:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

4. **Use Docker secrets** cho sensitive data thay vì .env file

5. **Regular backups** cho MongoDB volume

---

## 📚 API Documentation

Sau khi khởi động server, truy cập Swagger UI để xem đầy đủ API documentation và test endpoints:

👉 **http://localhost:8000/docs**

### Main Endpoints

| Method | Endpoint                      | Description                         |
| ------ | ----------------------------- | ----------------------------------- |
| GET    | `/health`                     | Health check endpoint               |
| POST   | `/api/v1/ai/voice/transcribe` | Chuyển đổi audio thành text         |
| POST   | `/api/v1/ai/voice/extract`    | Trích xuất thông tin từ audio       |
| POST   | `/api/v1/ai/bill/extract`     | Trích xuất thông tin từ ảnh hóa đơn |
| GET    | `/api/v1/ai/bill/{id}`        | Lấy thông tin bill theo ID          |
| GET    | `/api/v1/ai/voice/{id}`       | Lấy thông tin voice theo ID         |

---

## 🔒 Security Best Practices

- ⚠️ **KHÔNG BAO GIỜ** commit file `.env` vào Git
- 🔑 Sử dụng strong passwords cho MongoDB
- 🛡️ Rotate API keys định kỳ
- 📝 Review logs thường xuyên để phát hiện anomalies
- 🚫 Không expose sensitive data trong logs
- 🔐 Sử dụng HTTPS trong production
- 👥 Implement rate limiting cho public APIs

---

## 📊 Monitoring & Logging

**Logs location:**

- Development: Console output
- Docker: `docker compose logs -f`
- Production: Configure external logging service

**Health monitoring:**

```bash
# Simple health check
curl http://localhost:8000/health

# Detailed monitoring với watch
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

[MIT License](LICENSE)

---

## 👥 Team

**Vicobi Development Team**

Made with ❤️ by Vicobi Team
