# 🚀 Vicobi AI

**Vicobi AI** là một API dịch vụ xử lý giọng nói và hóa đơn sử dụng AI, được xây dựng với FastAPI, MongoDB và Google Gemini AI.

## ✨ Tính năng

- 🎤 **Voice Processing**: Xử lý và phân tích giọng nói
- 📄 **Bill/Invoice Extraction**: Trích xuất thông tin từ hóa đơn bằng AI (Gemini, PaddleOCR)
- 🗄️ **MongoDB Integration**: Lưu trữ dữ liệu với MongoDB
- 🔒 **Secure Configuration**: Quản lý biến môi trường với `.env`
- 📚 **Auto Documentation**: API docs tự động với Swagger UI

## 🛠️ Công nghệ

- **FastAPI**: Web framework hiện đại, hiệu suất cao
- **MongoDB**: NoSQL database
- **Google Gemini AI**: AI model cho trích xuất thông tin
- **PaddleOCR**: OCR engine cho tiếng Việt
- **Pydantic**: Data validation
- **Loguru**: Logging system

## 📋 Yêu cầu

- Python 3.10+
- MongoDB (Docker hoặc local)
- Google Gemini API Key

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone https://gitlab.com/vicobi/vicobi-ai.git
cd vicobi-ai
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc
venv\\Scripts\\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

Sao chép file `.env-example` thành `.env` và cập nhật các giá trị:

```bash
cp .env-example .env
```

Chỉnh sửa file `.env`:

```env
# MongoDB
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_INITDB_ROOT_PASSWORD=your_secure_password
MONGO_INITDB_DATABASE=VicobiMongoDB

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Khởi động MongoDB (Docker)

```bash
docker compose up -d
```

Hoặc cài đặt MongoDB local:

```bash
# macOS
brew install mongodb-community
brew services start mongodb-community
```

### 6. Chạy ứng dụng

```bash
uvicorn app.main:app --reload
```

API sẽ chạy tại: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📁 Cấu trúc Project

```
vicobi-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # MongoDB connection
│   ├── utils.py                # Utility functions
│   ├── routers/                # API endpoints
│   │   ├── voice.py
│   │   └── bill.py
│   ├── models/                 # Database models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── voice_service.py
│   │   └── gemini_extractor/
│   └── src/                    # OCR & AI models
├── uploads/                    # Upload directory
├── logs/                       # Log files
├── .env                        # Environment variables (not in git)
├── .env-example                # Example environment file
├── requirements.txt            # Python dependencies
└── docker-compose.yml          # Docker configuration
```

## 🔧 Configuration

Tất cả cấu hình được quản lý thông qua file `.env`. Xem `.env-example` để biết danh sách đầy đủ các biến môi trường.

### Các biến môi trường chính:

| Biến             | Mô tả                               | Mặc định    |
| ---------------- | ----------------------------------- | ----------- |
| `PROJECT_NAME`   | Tên project                         | VicobiAI    |
| `API_PREFIX`     | API route prefix                    | /api/v1     |
| `ENVIRONMENT`    | Môi trường (development/production) | development |
| `MONGO_HOST`     | MongoDB host                        | localhost   |
| `MONGO_PORT`     | MongoDB port                        | 27017       |
| `GEMINI_API_KEY` | Google Gemini API key               | (required)  |
| `LOG_LEVEL`      | Logging level                       | INFO        |

## 📝 API Endpoints

### Health Check

```bash
GET /health
```

### Voice Processing

```bash
POST /api/v1/voice/transcribe
```

### Bill Processing

```bash
POST /api/v1/bill/extract
```

Chi tiết đầy đủ tại: `http://localhost:8000/docs`

## 🧪 Testing

```bash
pytest
```

## 📊 Logging

Logs được lưu tại `logs/api.log` với rotation tự động:

- Rotation size: 500 MB
- Retention: 10 days

## 🐳 Docker

### Build và chạy với Docker Compose

```bash
docker compose up -d
```

### Dừng services

```bash
docker compose down
```

## 🔒 Security

- ⚠️ **KHÔNG** commit file `.env` vào git
- 🔑 Sử dụng API keys mạnh và bảo mật
- 🛡️ Enable CORS chỉ cho các origins tin cậy
- 📝 Review logs thường xuyên

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [Google Gemini API](https://ai.google.dev/)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

[MIT License](LICENSE)

## 👥 Team

Vicobi Development Team

---

Made with ❤️ by Vicobi Team

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name

Choose a self-explaining name for your project.

## Description

Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges

On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals

Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation

Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage

Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support

Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap

If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing

State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment

Show your appreciation to those who have contributed to the project.

## License

For open source projects, say how it is licensed.

## Project status

If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
