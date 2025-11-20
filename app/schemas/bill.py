"""
Bill schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class ExtractionResponse(BaseModel):
    """Response model for single extraction"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    job_id: Optional[str] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    extractor_initialized: bool
    config_loaded: bool
    model_version: Optional[str] = None
