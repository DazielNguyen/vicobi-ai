from fastapi import UploadFile

def is_bill(file_bytes: bytes) -> bool:
    """Kiểm tra xem file có phải là hóa đơn không dựa trên phần mở rộng"""
    
    return True

def extract_bill_using_ocr_model(file_path: str) -> dict:
    """Trích xuất dữ liệu hóa đơn từ file hình ảnh sử dụng mô hình OCR"""
    
    return {"extracted_data": "OCR data"}