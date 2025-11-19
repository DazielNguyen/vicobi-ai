from fastapi import FastAPI
from fastapi.responses import RedirectResponse

# Import routers
from app.routers import voice
from app.database import lifespan

app = FastAPI(
    title="Vicobi AI API",
    description="API for voice and bill processing",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(voice.router)

