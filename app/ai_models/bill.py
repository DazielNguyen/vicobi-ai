from pathlib import Path
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
    print("Model đã load thành công từ local (tương đối).")
except Exception as e:
    print(f"Lỗi khi load model: {e}")

IMG_SIZE = 224
THRESHOLD = 0.85
transform_inference = T.Compose([
    T.Resize(256),
    T.CenterCrop(IMG_SIZE),
    T.ToTensor(),
])
def is_bill(file_bytes: bytes) -> bool:
    
    img_pil = Image.open(io.BytesIO(file_bytes)).convert('RGB')
    img_tensor = transform_inference(img_pil).unsqueeze(0).to(device)

    loaded_model.eval()
    with torch.no_grad():
        output_logit = loaded_model(img_tensor)
        P_NOT_BILL = torch.sigmoid(output_logit).item()
        P_BILL = 1 - P_NOT_BILL

    return P_BILL >= THRESHOLD or (P_BILL > P_NOT_BILL)

# Hàm trích xuất OCR
def extract_bill_using_ocr_model(file_path: str) -> dict:
    return {"extracted_data": "OCR data"}
