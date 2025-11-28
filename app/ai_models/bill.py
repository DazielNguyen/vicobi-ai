from pathlib import Path
import cv2
import easyocr
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
import torchvision.transforms as T
from app.config import settings
import io
import os

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

BASE_DIR = Path(__file__).parent
SAVE_DIR = BASE_DIR / "saved_models"
MODEL_BILL_FILE_NAME = settings.MODEL_BILL_FILE_NAME
MODEL_PATH = SAVE_DIR / MODEL_BILL_FILE_NAME

base_model = models.mobilenet_v2(weights=None)
for param in base_model.parameters():
    param.requires_grad = False

num_ftrs = base_model.last_channel
classifier_head = nn.Sequential(
    nn.Dropout(0.2),
    nn.Linear(num_ftrs, 128),
    nn.ReLU(),
    nn.Linear(128, 1)
)
base_model.classifier = classifier_head
loaded_model = base_model.to(device)

try:
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    loaded_model.load_state_dict(checkpoint['model_state_dict'])
    loaded_model.eval()
except Exception as e:
    print(f"Lỗi khi load model: {e}")

THRESHOLD = 0.85
transform_inference = T.Compose([
    T.ToTensor(), 
])
ocr_reader = easyocr.Reader(['en', 'vi'])

def is_bill_model_ready() -> bool:
    """Kiểm tra xem model có load thành công và inference được không"""
    if loaded_model is None:
        return False
    try:
        dummy = torch.zeros(1, 3, 224, 224).to(device)
        loaded_model.eval()
        with torch.no_grad():
            _ = loaded_model(dummy)
        return True
    except Exception:
        return False

def is_bill(file_bytes: bytes) -> bool:
    """
    Nhận file bytes đã được frontend crop/resize,
    trả về True nếu là hóa đơn, False nếu không.
    """
    img_pil = Image.open(io.BytesIO(file_bytes)).convert('RGB')
    img_tensor = transform_inference(img_pil).unsqueeze(0).to(device)

    loaded_model.eval()
    with torch.no_grad():
        output_logit = loaded_model(img_tensor)
        P_NOT_BILL = torch.sigmoid(output_logit).item()
        P_BILL = 1 - P_NOT_BILL

    return P_BILL >= THRESHOLD or (P_BILL > P_NOT_BILL)



# Hàm trích xuất OCR
def extract_bill_using_ocr_model(file_path: str, save_result_img: bool = False) -> str:
    """
    Nhận đường dẫn file ảnh hóa đơn (đã được frontend xử lý), trả về dict dữ liệu trích xuất từ OCR.
    - file_path: đường dẫn file ảnh
    - save_result_img: True để lưu ảnh có bounding box
    """
    # 1. Đọc ảnh
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    # 2. OCR với EasyOCR
    results = ocr_reader.readtext(img)

    extracted_texts = []
    LINE_COLOR = (0, 255, 0)  # Xanh lá (BGR)
    THICKNESS = 2

    # 3. Vẽ bounding box và lưu văn bản + độ tin cậy
    for (bbox, text, prob) in results:
        top_left = tuple([int(val) for val in bbox[0]])
        bottom_right = tuple([int(val) for val in bbox[2]])
        cv2.rectangle(img, top_left, bottom_right, LINE_COLOR, THICKNESS)

        extracted_texts.append({
            "text": text,
            "confidence": float(prob),
            "bbox": [top_left, bottom_right]
        })

    # 4. Lưu ảnh kết quả nếu cần
    if save_result_img:
        ext = file_path.split('.')[-1]
        result_img_path = file_path.replace(f".{ext}", f"_ocr.{ext}")
        cv2.imwrite(result_img_path, img)

    return extracted_texts
