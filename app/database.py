from contextlib import asynccontextmanager
from mongoengine import connect, disconnect
from app.config import settings
from fastapi import FastAPI


MONGO_INITDB_ROOT_USERNAME = settings.MONGO_INITDB_ROOT_USERNAME
MONGO_INITDB_ROOT_PASSWORD = settings.MONGO_INITDB_ROOT_PASSWORD
MONGO_INITDB_DATABASE = settings.MONGO_INITDB_DATABASE
MONGO_DB_URL = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@localhost:27017/{MONGO_INITDB_DATABASE}?authSource=admin"

# Global flag to track MongoDB connection status
mongodb_available = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle cho FastAPI — kết nối MongoDB khi khởi động và ngắt khi tắt"""
    global mongodb_available
    
    try:
        print("Connecting to MongoDB...")
        connect(
            db=MONGO_INITDB_DATABASE, 
            host=MONGO_DB_URL, 
            alias="default",
            serverSelectionTimeoutMS=5000,  # Timeout nhanh để không chờ lâu
            connectTimeoutMS=5000
        )
        mongodb_available = True
        print("✓ MongoDB connected successfully!")
    except Exception as e:
        mongodb_available = False
        print(f"⚠️  MongoDB connection failed: {e}")
        print("⚠️  API will run WITHOUT MongoDB (transcription-only mode)")
        print("💡 To enable MongoDB:")
        print("   - Option 1: Start Docker Desktop + docker compose up -d")
        print("   - Option 2: Install MongoDB locally + brew services start mongodb-community")

    yield

    if mongodb_available:
        print("Disconnecting MongoDB...")
        try:
            disconnect(alias="default")
        except:
            pass