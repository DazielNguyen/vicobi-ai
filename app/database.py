from contextlib import asynccontextmanager
from mongoengine import connect, disconnect
from app.config import settings
from fastapi import FastAPI


MONGO_INITDB_ROOT_USERNAME = settings.MONGO_INITDB_ROOT_USERNAME
MONGO_INITDB_ROOT_PASSWORD = settings.MONGO_INITDB_ROOT_PASSWORD
MONGO_INITDB_DATABASE = settings.MONGO_INITDB_DATABASE
MONGO_DB_URL = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@localhost:27017/{MONGO_INITDB_DATABASE}?authSource=admin"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle cho FastAPI — kết nối MongoDB khi khởi động và ngắt khi tắt"""
    print("Connecting to MongoDB...")
    connect(db=MONGO_INITDB_DATABASE, host=MONGO_DB_URL, alias="default")

    yield

    print("Disconnecting MongoDB...")
    disconnect(alias="default")