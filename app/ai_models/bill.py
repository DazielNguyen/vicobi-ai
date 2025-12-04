from pathlib import Path
import cv2
import easyocr
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
import torchvision.transforms as T
from loguru import logger
from app.config import settings
import io

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

BASE_DIR = Path(__file__).parent
SAVE_DIR = BASE_DIR / "saved_models"
MODEL_BILL_FILE_NAME = settings.MODEL_BILL_FILE_NAME
MODEL_PATH = SAVE_DIR / MODEL_BILL_FILE_NAME

if 'v1' in MODEL_BILL_FILE_NAME.lower():
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
    
else:
    base_model = models.efficientnet_b0(weights=None)
    
    num_ftrs = base_model.classifier[1].in_features
    
    base_model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(num_ftrs, 128),
        nn.ReLU(),
        nn.Dropout(p=0.3), 
        nn.Linear(128, 1)
    )

loaded_model = base_model.to(device)

try:
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    loaded_model.load_state_dict(checkpoint['model_state_dict'])
    loaded_model.eval()
except Exception as e:
    logger.error(f"Error loading bill classifier model: {e}")

THRESHOLD = 0.85
transform_inference = T.Compose([
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
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
    """Classify image bytes to determine if it's a valid bill/invoice"""
    img_pil = Image.open(io.BytesIO(file_bytes)).convert('RGB')
    img_tensor = transform_inference(img_pil).unsqueeze(0).to(device)

    loaded_model.eval()
    with torch.no_grad():
        output_logit = loaded_model(img_tensor)
        P_NOT_BILL = torch.sigmoid(output_logit).item()
        P_BILL = 1 - P_NOT_BILL

    return P_BILL >= THRESHOLD or (P_BILL > P_NOT_BILL)

# Hàm trích xuất OCR
def extract_bill_using_ocr_model(file_path: str) -> str:
    """Extract text from bill image using EasyOCR"""
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    results = ocr_reader.readtext(img)

    extracted_texts = []
    LINE_COLOR = (0, 255, 0)
    THICKNESS = 2

    for (bbox, text, prob) in results:
        top_left = tuple([int(val) for val in bbox[0]])
        bottom_right = tuple([int(val) for val in bbox[2]])
        cv2.rectangle(img, top_left, bottom_right, LINE_COLOR, THICKNESS)

        extracted_texts.append({
            "text": text,
            "confidence": float(prob),
            "bbox": [top_left, bottom_right]
        })

    return extracted_texts
