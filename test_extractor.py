#!/usr/bin/env python3
"""Test script to check if extractor can be initialized"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from loguru import logger
from app.src.gemini_extractor.config import load_config
from app.src.gemini_extractor.pipeline import GeminiInvoiceExtractor, BatchProcessor

def test_initialization():
    try:
        # Load config
        logger.info("Loading config...")
        config = load_config()
        
        # Validate
        logger.info("Validating config...")
        if not config.validate():
            logger.error("Config validation failed")
            return False
        
        # Initialize extractor
        logger.info("Initializing extractor...")
        extractor = GeminiInvoiceExtractor(config)
        
        logger.success("✅ Extractor initialized successfully!")
        logger.info(f"Model: {config.get('api.model_version')}")
        
        # Test batch processor
        logger.info("Initializing batch processor...")
        batch_processor = BatchProcessor(extractor)
        logger.success("✅ Batch processor initialized!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_initialization()
    sys.exit(0 if success else 1)
