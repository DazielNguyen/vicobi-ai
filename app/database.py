"""
Database Configuration

MongoDB connection management with FastAPI lifespan.
"""
from contextlib import asynccontextmanager
from mongoengine import connect, disconnect
from loguru import logger
from fastapi import FastAPI

from app.config import settings


# Global flag to track MongoDB connection status
mongodb_available = False


def is_mongodb_connected() -> bool:
    """Trả về trạng thái kết nối MongoDB hiện tại"""
    return mongodb_available


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI application.
    Connects to MongoDB on startup and disconnects on shutdown.
    """
    global mongodb_available
    
    try:
        logger.info("🔌 Connecting to MongoDB...")
        connect(
            db=settings.MONGO_INITDB_DATABASE, 
            host=settings.mongo_uri, 
            alias="default",
            serverSelectionTimeoutMS=5000,  # Quick timeout
            connectTimeoutMS=5000
        )
        mongodb_available = True
        logger.success(f"✅ MongoDB connected: {settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_INITDB_DATABASE}")
    except Exception as e:
        mongodb_available = False
        logger.warning(f"⚠️  MongoDB connection failed: {e}")

    yield

    # Cleanup on shutdown
    if mongodb_available:
        logger.info("🔌 Disconnecting MongoDB...")
        try:
            disconnect(alias="default")
            logger.success("✅ MongoDB disconnected")
        except Exception as e:
            logger.error(f"❌ Failed to disconnect MongoDB: {e}")