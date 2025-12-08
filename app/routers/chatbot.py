from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.auth import verify_admin, verify_jwt
from app.config import settings
from app.database import is_mongodb_connected
from app.services.chatbot_service import ChatbotService
from app.schemas.chatbot import ChatRequest, ChatResponse

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/chatbot",
    tags=["chatbot"],
)

chatbot_service: Optional[ChatbotService] = None
limiter = Limiter(key_func=get_remote_address)

def get_service():
    if not chatbot_service:
        raise HTTPException(status_code=503, detail="Chatbot Service not initialized")
    return chatbot_service

@router.get("/health")
async def health_check(
    user=Depends(verify_jwt),
    service: ChatbotService = Depends(get_service)
):
    """Kiểm tra trạng thái Chatbot Service (chỉ admin)"""
    bedrock_ready = service.bedrock_extractor is not None
    qdrant_ready = service.vector_store is not None
    mongo_ready = is_mongodb_connected()

    return {
        "status": "healthy" if (bedrock_ready and qdrant_ready) and mongo_ready else "degraded",
        "providers": {
            "bedrock": "connected" if bedrock_ready else "not_configured",
            "qdrant": "connected" if qdrant_ready else "not_configured"
        },
        "mongodb": "connected" if mongo_ready else "disconnected"
    }

@router.get("/files")
async def get_files_list(
    user=Depends(verify_admin),
    service: ChatbotService = Depends(get_service)
):
    """Lấy danh sách các file đã được ingest vào Qdrant (chỉ admin)"""
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
    return service.get_files_list()

@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    user=Depends(verify_admin),
    service: ChatbotService = Depends(get_service)
):
    """Nạp dữ liệu từ file txt hoặc pdf vào Qdrant vector store (chỉ admin)"""
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
    if not file.filename.endswith(('.txt', '.pdf')):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file .txt hoặc .pdf")
    
    try:
        content = await file.read()
        result = await service.ingest_from_file(content, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý file: {str(e)}")

@router.post("/ask", response_model=ChatResponse)
@limiter.limit(f"{settings.RATE_LIMIT_TIMES}/{settings.RATE_LIMIT_SECONDS}seconds")
async def ask(
    request: Request,
    req: ChatRequest,
    user=Depends(verify_jwt),
    service: ChatbotService = Depends(get_service)
):
    """Hỏi đáp với chatbot sử dụng RAG (member & admin)"""
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
    answer = service.ask(req.question)
    return ChatResponse(answer=answer)

@router.delete("/files/{filename}")
async def delete_file(
    filename: str,
    user=Depends(verify_admin),
    service: ChatbotService = Depends(get_service)
):
    """Xóa một file cụ thể khỏi Qdrant vector store (chỉ admin)"""
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
    result = service.delete_file(filename)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

@router.delete("/reset")
async def reset(
    user=Depends(verify_admin),
    service: ChatbotService = Depends(get_service)
):
    """Xóa toàn bộ dữ liệu trong Qdrant collection (chỉ admin)"""
    cog_sub = user.get("sub")
    if not cog_sub:
        raise HTTPException(status_code=401, detail="User chưa được xác thực")
    
    return service.clear_memory()