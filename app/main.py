from fastapi import FastAPI
from app.routers import bill, voice
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import lifespan

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(bill.router)
app.include_router(voice.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to VicobiAI API"}