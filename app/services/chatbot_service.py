from typing import List, Dict, Any, Optional
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.services.bedrock_extractor.chatbot import BedrockChatExtractor
from app.ai_models.embeddings import get_embedding_model, get_embedding_dimension
from app.config import settings
import PyPDF2
import io
from datetime import datetime

class ChatbotService:
    """RAG Chatbot service using AWS Bedrock and Qdrant"""

    def __init__(self, bedrock_extractor: Optional[BedrockChatExtractor] = None):
        self.qdrant_url = settings.QDRANT_URL
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.bedrock_extractor = bedrock_extractor
        self.embedding_model = get_embedding_model()
        self.embedding_dimension = get_embedding_dimension()
        self.vector_store = self._initialize_vector_store()

    def _initialize_vector_store(self) -> QdrantVectorStore:
        """Connect to Qdrant and create collection if not exists"""
        client = QdrantClient(url=self.qdrant_url, prefer_grpc=False)
        
        if not client.collection_exists(self.collection_name):
            print(f"Creating Qdrant collection: {self.collection_name}")
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_dimension, 
                    distance=models.Distance.COSINE
                ),
            )
            
        return QdrantVectorStore(
            client=client,
            collection_name=self.collection_name,
            embedding=self.embedding_model,
        )

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Trích xuất text từ file PDF"""
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_content = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text.strip():
                text_content.append(text)
        
        return "\n\n".join(text_content)
    
    def _extract_text_from_txt(self, file_content: bytes) -> str:
        """Trích xuất text từ file TXT"""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            # Thử với encoding khác nếu utf-8 thất bại
            return file_content.decode('latin-1')
    
    async def ingest_from_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Ingest data from TXT or PDF file into Qdrant vector store"""
        try:
            # Trích xuất text từ file
            if filename.endswith('.pdf'):
                text_content = self._extract_text_from_pdf(file_content)
            elif filename.endswith('.txt'):
                text_content = self._extract_text_from_txt(file_content)
            else:
                return {"status": "error", "message": "Định dạng file không được hỗ trợ"}
            
            if not text_content.strip():
                return {"status": "warning", "message": "File không có nội dung"}
            
            # Chia text thành các chunks nhỏ hơn (tùy chọn)
            # Ở đây ta có thể chia theo đoạn văn hoặc theo số ký tự
            chunks = self._split_text_into_chunks(text_content)
            
            # Tạo metadata cho mỗi chunk
            timestamp = datetime.now().isoformat()
            metadatas = [
                {
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "uploaded_at": timestamp,
                    "source": filename  # Thêm field 'source' để tương thích với langchain
                }
                for i in range(len(chunks))
            ]
            
            # Thêm vào vector store với metadata
            print(f"Adding {len(chunks)} chunks with metadata for file: {filename}")
            ids = self.vector_store.add_texts(texts=chunks, metadatas=metadatas)
            print(f"Successfully added {len(ids)} chunks to Qdrant")
            
            return {
                "status": "success",
                "filename": filename,
                "indexed_count": len(chunks),
                "total_characters": len(text_content),
                "uploaded_at": timestamp
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Chia text thành các chunks nhỏ với overlap"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Tìm dấu kết thúc câu gần nhất
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                split_point = max(last_period, last_newline)
                
                if split_point > chunk_size // 2:
                    chunk = chunk[:split_point + 1]
                    end = start + split_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def ingest_knowledge(self, texts: List[str]) -> Dict[str, Any]:
        """Ingest text data into Qdrant vector store (legacy method)"""
        if not texts:
            return {"status": "warning", "message": "Danh sách text rỗng"}
            
        try:
            self.vector_store.add_texts(texts)
            return {"status": "success", "indexed_count": len(texts)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def ask(self, question: str) -> str:
        """RAG process: Retrieve similar vectors, contextualize, and generate response"""
        if not self.bedrock_extractor:
            return "Lỗi: Bedrock Chat Extractor chưa được khởi tạo."

        try:
            docs = self.vector_store.similarity_search(question, k=3)
            
            if not docs:
                return "Xin lỗi, tôi không tìm thấy thông tin liên quan trong dữ liệu."

            context_text = "\n\n".join([d.page_content for d in docs])
            
            answer = self.bedrock_extractor.generate_response(
                context=context_text, 
                question=question
            )
            return answer

        except Exception as e:
            return f"Đã xảy ra lỗi hệ thống: {str(e)}"
    
    def get_files_list(self) -> Dict[str, Any]:
        """Lấy danh sách các file đã được ingest vào Qdrant"""
        try:
            client = QdrantClient(url=self.qdrant_url, prefer_grpc=False)
            
            # Scroll through all points to get unique filenames
            scroll_result = client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Tăng limit để lấy nhiều points hơn
                with_payload=True,
                with_vectors=False
            )
            
            points = scroll_result[0]
            
            # Debug: In ra payload của một số points
            if points:
                print(f"Total points found: {len(points)}")
                print(f"Sample point payload: {points[0].payload if points else 'No points'}")
            
            # Group by filename and get stats
            files_dict = {}
            for point in points:
                payload = point.payload or {}
                
                # Kiểm tra cả 'filename' và 'metadata.filename'
                filename = payload.get('filename') or payload.get('metadata', {}).get('filename')
                
                if filename:
                    uploaded_at = payload.get('uploaded_at') or payload.get('metadata', {}).get('uploaded_at', 'Unknown')
                    
                    if filename not in files_dict:
                        files_dict[filename] = {
                            "filename": filename,
                            "chunks_count": 0,
                            "uploaded_at": uploaded_at
                        }
                    files_dict[filename]["chunks_count"] += 1
            
            files_list = sorted(files_dict.values(), key=lambda x: x.get('uploaded_at', ''), reverse=True)
            
            return {
                "status": "success",
                "total_files": len(files_list),
                "total_points": len(points),
                "files": files_list
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Lấy thông tin về collection trong Qdrant"""
        try:
            client = QdrantClient(url=self.qdrant_url, prefer_grpc=False)
            collection_info = client.get_collection(self.collection_name)
            
            return {
                "status": "success",
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.indexed_vectors_count,
                "segments_count": collection_info.segments_count,
                "collection_status": collection_info.status.value if hasattr(collection_info.status, 'value') else str(collection_info.status)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def delete_file(self, filename: str) -> Dict[str, Any]:
        """Xóa tất cả các chunks của một file cụ thể"""
        try:
            client = QdrantClient(url=self.qdrant_url, prefer_grpc=False)
            
            # Lấy tất cả points và filter bằng Python vì cấu trúc payload phức tạp
            scroll_result = client.scroll(
                collection_name=self.collection_name,
                limit=10000,
                with_payload=True,
                with_vectors=False
            )
            
            points = scroll_result[0]
            
            # Filter points có filename khớp
            matching_point_ids = []
            for point in points:
                payload = point.payload or {}
                # Kiểm tra cả 'filename' trực tiếp và 'metadata.filename'
                point_filename = payload.get('filename') or payload.get('metadata', {}).get('filename')
                
                if point_filename == filename:
                    matching_point_ids.append(point.id)
            
            if not matching_point_ids:
                return {
                    "status": "error",
                    "message": f"Không tìm thấy file '{filename}' trong hệ thống"
                }
            
            # Xóa tất cả points tìm được
            client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=matching_point_ids
                )
            )
            
            return {
                "status": "success",
                "message": f"Đã xóa file '{filename}'",
                "deleted_chunks": len(matching_point_ids)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def clear_memory(self):
        """Xóa toàn bộ dữ liệu trong collection"""
        client = QdrantClient(url=self.qdrant_url)
        client.delete_collection(self.collection_name)
        self.vector_store = self._initialize_vector_store()
        return {"status": "cleared"}

_chatbot_service_instance = None

def get_chatbot_service_instance(bedrock_extractor: Optional[BedrockChatExtractor] = None):
    global _chatbot_service_instance
    if _chatbot_service_instance is None and bedrock_extractor:
        _chatbot_service_instance = ChatbotService(bedrock_extractor)
    return _chatbot_service_instance