import shutil
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import extractor components
from app.src.gemini_extractor.pipeline import GeminiInvoiceExtractor, BatchProcessor
from app.src.gemini_extractor.config import load_config

# Import routers
from app.routers import voice, bill
from app.database import lifespan

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize global variables
config = None
extractor = None
batch_processor = None

# Directory structure
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
TEMP_DIR = Path("temp")

# Load config
try:
    config = load_config()
    logger.info("✅ Configuration loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load configuration: {e}")
    logger.warning("⚠️ Extractor will be initialized without config")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Vicobi AI API",
    description="API for voice and bill processing",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(voice.router)
app.include_router(bill.router)

# Share global variables with bill router
bill.config = config
bill.extractor = None  # Will be set in startup
bill.batch_processor = None  # Will be set in startup
bill.UPLOAD_DIR = UPLOAD_DIR
bill.OUTPUT_DIR = OUTPUT_DIR
bill.TEMP_DIR = TEMP_DIR


# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize extractor on startup"""
    global extractor, batch_processor
    
    logger.info("🚀 Starting Vicobi AI API...")
    
    # Create directories
    UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    TEMP_DIR.mkdir(exist_ok=True, parents=True)
    
    try:
        logger.info(f"Config is None: {config is None}")
        if config is None:
            raise ValueError("Configuration not loaded")
        
        # Validate API key is set
        logger.info("Validating configuration...")
        validation_result = config.validate()
        logger.info(f"Validation result: {validation_result}")
        
        if not validation_result:
            raise ValueError("Configuration validation failed")
        
        # Initialize extractor
        logger.info("Creating GeminiInvoiceExtractor...")
        extractor = GeminiInvoiceExtractor(config)
        logger.info("Creating BatchProcessor...")
        batch_processor = BatchProcessor(extractor)
        
        # Share with bill router
        bill.extractor = extractor
        bill.batch_processor = batch_processor
        
        logger.info("✅ Extractor initialized successfully")
        logger.info(f"📋 Model: {config.get('api.model_version')}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize extractor: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        logger.warning("⚠️ API will start but extraction endpoints will not work")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down API...")
    
    # Clean up temporary files
    try:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        TEMP_DIR.mkdir(exist_ok=True)
        logger.info("🧹 Cleaned up temporary files")
    except Exception as e:
        logger.error(f"Failed to clean up temp files: {e}")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - redirect to docs"""
    return RedirectResponse(url="/docs")
