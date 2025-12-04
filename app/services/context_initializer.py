"""
Context Initializer Service

Tự động ingest các file context từ folder context vào Qdrant khi khởi động app lần đầu.
"""
import os
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger
from app.services.chatbot_service import ChatbotService


class ContextInitializer:
    """Service để tự động load context files vào vector store"""
    
    def __init__(self, chatbot_service: ChatbotService):
        self.chatbot_service = chatbot_service
        self.context_folder = Path(__file__).parent.parent / "ai_models" / "contexts"
        self.supported_extensions = {".pdf", ".txt"}
    
    def _get_context_files(self) -> List[Path]:
        """Lấy danh sách các file context cần được ingest"""
        if not self.context_folder.exists():
            logger.warning(f"Context folder không tồn tại: {self.context_folder}")
            return []
        
        context_files = []
        for file_path in self.context_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                context_files.append(file_path)
        
        return context_files
    
    def _is_file_already_indexed(self, filename: str) -> bool:
        """Kiểm tra xem file đã được index chưa"""
        try:
            files_list = self.chatbot_service.get_files_list()
            if files_list.get("status") == "success":
                indexed_files = [f["filename"] for f in files_list.get("files", [])]
                return filename in indexed_files
            return False
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra file đã index: {e}")
            return False
    
    async def initialize_context_files(self) -> Dict[str, Any]:
        """
        Ingest tất cả các file trong folder context vào vector store.
        Chỉ ingest các file chưa được index.
        """
        context_files = self._get_context_files()
        
        if not context_files:
            logger.info("Không có file context nào cần ingest")
            return {
                "status": "success",
                "message": "Không có file context",
                "files_processed": 0,
                "files_skipped": 0,
                "files_failed": 0
            }
        
        results = {
            "processed": [],
            "skipped": [],
            "failed": [],
        }
        
        logger.info(f"Tìm thấy {len(context_files)} file(s) trong folder context")
        
        for file_path in context_files:
            filename = file_path.name
            
            try:
                # Kiểm tra xem file đã được index chưa
                if self._is_file_already_indexed(filename):
                    logger.info(f"⏭️  File '{filename}' đã được index, bỏ qua")
                    results["skipped"].append(filename)
                    continue
                
                logger.info(f"📄 Đang ingest file: {filename}")
                
                # Đọc nội dung file
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Ingest file vào vector store
                result = await self.chatbot_service.ingest_from_file(
                    file_content=file_content,
                    filename=filename
                )
                
                if result.get("status") == "success":
                    logger.success(f"✅ Đã ingest '{filename}': {result.get('indexed_count')} chunks")
                    results["processed"].append({
                        "filename": filename,
                        "chunks": result.get("indexed_count"),
                        "size": len(file_content)
                    })
                else:
                    logger.error(f"❌ Lỗi ingest '{filename}': {result.get('message')}")
                    results["failed"].append({
                        "filename": filename,
                        "error": result.get("message")
                    })
            
            except Exception as e:
                logger.error(f"❌ Lỗi xử lý file '{filename}': {str(e)}")
                results["failed"].append({
                    "filename": filename,
                    "error": str(e)
                })
        
        summary = {
            "status": "success",
            "message": f"Hoàn thành ingest context files",
            "files_processed": len(results["processed"]),
            "files_skipped": len(results["skipped"]),
            "files_failed": len(results["failed"]),
            "details": results
        }
        
        logger.info(
            f"📊 Context Initialization Summary: "
            f"{len(results['processed'])} processed, "
            f"{len(results['skipped'])} skipped, "
            f"{len(results['failed'])} failed"
        )
        
        return summary


async def auto_initialize_context(chatbot_service: ChatbotService) -> Dict[str, Any]:
    """
    Helper function để tự động initialize context files.
    Gọi hàm này trong app startup.
    """
    initializer = ContextInitializer(chatbot_service)
    return await initializer.initialize_context_files()
