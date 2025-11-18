"""
Service để phân tích transcription text và tách thành nhiều transactions
"""
import re
from typing import List, Dict, Tuple
from datetime import datetime


class TransactionParser:
    """Parser để tách transcription thành nhiều giao dịch riêng biệt"""
    
    # Từ khóa chỉ chi tiêu
    EXPENSE_KEYWORDS = [
        'mua', 'chi', 'trả', 'mất', 'tốn', 'nộp', 'đóng', 
        'tiêu', 'phí', 'uống', 'ăn', 'thuê'
    ]
    
    # Từ khóa chỉ thu nhập
    INCOME_KEYWORDS = [
        'thu', 'nhận', 'được', 'kiếm', 'lương', 'bán', 
        'làm', 'thu nhập', 'kiếm được', 'được trả'
    ]
    
    # Pattern để tìm số tiền
    MONEY_PATTERNS = [
        r'(\d+)\s*(?:triệu|tr)',  # X triệu
        r'(\d+)\s*(?:nghìn|k|ngàn)',  # X nghìn
        r'(\d+)\s*(?:trăm)',  # X trăm
        r'(\d+[\.,]\d+)\s*(?:triệu|tr)',  # X.Y triệu
        r'(\d+[\.,]\d+)\s*(?:nghìn|k|ngàn)',  # X.Y nghìn
        # Số bằng chữ
        r'(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(?:triệu|nghìn|trăm)',
        r'(hai mươi|ba mươi|bốn mươi|năm mươi|sáu mươi|bảy mươi|tám mươi|chín mươi)\s+(?:lăm|mốt|mươi)?\s*(?:nghìn)?',
    ]
    
    # Mapping số chữ -> số
    WORD_TO_NUMBER = {
        'không': 0, 'một': 1, 'hai': 2, 'ba': 3, 'bốn': 4,
        'năm': 5, 'sáu': 6, 'bảy': 7, 'tám': 8, 'chín': 9,
        'mười': 10, 'mươi': 10, 'trăm': 100, 'nghìn': 1000, 'ngàn': 1000,
        'triệu': 1000000, 'tr': 1000000, 'k': 1000,
        'lăm': 5, 'mốt': 1
    }
    
    @staticmethod
    def convert_text_to_number(text: str) -> float:
        """Chuyển đổi text tiền sang số"""
        text = text.lower().strip()
        
        # Kiểm tra số thập phân
        if re.match(r'^\d+[\.,]\d+$', text):
            return float(text.replace(',', '.'))
        
        # Kiểm tra số nguyên
        if text.isdigit():
            return float(text)
        
        # Chuyển đổi số bằng chữ
        words = text.split()
        result = 0
        current_number = 0
        
        for word in words:
            word = word.strip()
            if word in TransactionParser.WORD_TO_NUMBER:
                value = TransactionParser.WORD_TO_NUMBER[word]
                
                if value >= 1000:  # Đơn vị lớn (nghìn, triệu)
                    if current_number == 0:
                        current_number = 1
                    result += current_number * value
                    current_number = 0
                elif value >= 100:  # Trăm
                    current_number += value
                elif value >= 10:  # Mười
                    current_number += value
                else:  # Số đơn vị
                    current_number = current_number * 10 + value if current_number >= 10 else current_number + value
        
        result += current_number
        return float(result)
    
    @staticmethod
    def extract_amount_from_text(text: str) -> Tuple[float, str]:
        """
        Trích xuất số tiền từ text
        Returns: (amount, amount_string)
        """
        text = text.lower()
        
        # Thử các pattern
        for pattern in TransactionParser.MONEY_PATTERNS:
            match = re.search(pattern, text)
            if match:
                amount_string = match.group(0)
                try:
                    # Xử lý số
                    if 'triệu' in amount_string or 'tr' in amount_string:
                        num = TransactionParser.convert_text_to_number(
                            amount_string.replace('triệu', '').replace('tr', '').strip()
                        )
                        amount = num * 1000000
                    elif 'nghìn' in amount_string or 'ngàn' in amount_string or 'k' in amount_string:
                        num = TransactionParser.convert_text_to_number(
                            amount_string.replace('nghìn', '').replace('ngàn', '').replace('k', '').strip()
                        )
                        amount = num * 1000
                    elif 'trăm' in amount_string:
                        num = TransactionParser.convert_text_to_number(
                            amount_string.replace('trăm', '').strip()
                        )
                        amount = num * 100
                    else:
                        amount = TransactionParser.convert_text_to_number(amount_string)
                    
                    return (amount, amount_string)
                except:
                    continue
        
        return (0.0, "0")
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        Tách text thành các câu dựa vào từ khóa và số tiền
        """
        sentences = []
        
        # Tách theo dấu câu trước
        parts = re.split(r'[,\.;]', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Kiểm tra xem có chứa số tiền không
            has_amount = False
            for pattern in TransactionParser.MONEY_PATTERNS:
                if re.search(pattern, part.lower()):
                    has_amount = True
                    break
            
            if has_amount:
                sentences.append(part)
        
        # Nếu không tách được bằng dấu câu, thử tách bằng "tôi"
        if not sentences:
            parts = re.split(r'\btôi\b', text, flags=re.IGNORECASE)
            for i, part in enumerate(parts):
                if i > 0:  # Thêm lại "tôi" cho các part sau
                    part = "tôi " + part
                part = part.strip()
                if part and any(re.search(p, part.lower()) for p in TransactionParser.MONEY_PATTERNS):
                    sentences.append(part)
        
        return sentences if sentences else [text]
    
    @staticmethod
    def determine_transaction_type(sentence: str) -> str:
        """Xác định loại giao dịch (income/expense)"""
        sentence_lower = sentence.lower()
        
        # Kiểm tra từ khóa thu nhập
        for keyword in TransactionParser.INCOME_KEYWORDS:
            if keyword in sentence_lower:
                return "income"
        
        # Kiểm tra từ khóa chi tiêu
        for keyword in TransactionParser.EXPENSE_KEYWORDS:
            if keyword in sentence_lower:
                return "expense"
        
        # Mặc định là chi tiêu
        return "expense"
    
    @staticmethod
    def extract_description(sentence: str, amount_string: str) -> str:
        """Trích xuất mô tả từ câu"""
        # Loại bỏ các từ không cần thiết
        desc = sentence.lower()
        
        # Loại bỏ "tôi", "hôm nay", etc.
        remove_words = ['tôi', 'hôm nay', 'hôm qua', 'ngày', 'đã', 'bị', 'được', 'hết']
        for word in remove_words:
            desc = desc.replace(word, '')
        
        # Loại bỏ phần số tiền
        desc = desc.replace(amount_string.lower(), '')
        
        # Loại bỏ khoảng trắng thừa
        desc = ' '.join(desc.split()).strip()
        
        return desc if desc else "giao dịch"
    
    @staticmethod
    def parse(transcription_text: str) -> Dict:
        """
        Phân tích transcription và trả về structured data với nhiều transactions
        
        Returns:
            Dict with format:
            {
                "transactions": {
                    "incomes": [...],
                    "expenses": [...]
                },
                "total_amount": {
                    "incomes": float,
                    "expenses": float
                }
            }
        """
        # Tách thành các câu
        sentences = TransactionParser.split_into_sentences(transcription_text)
        
        incomes = []
        expenses = []
        
        for sentence in sentences:
            # Trích xuất số tiền
            amount, amount_string = TransactionParser.extract_amount_from_text(sentence)
            
            if amount <= 0:
                continue
            
            # Xác định loại giao dịch
            trans_type = TransactionParser.determine_transaction_type(sentence)
            
            # Trích xuất mô tả
            description = TransactionParser.extract_description(sentence, amount_string)
            
            # Tạo transaction object
            transaction = {
                "transaction_type": trans_type,
                "description": description,
                "amount": amount,
                "amount_string": amount_string,
                "quantity": 1.0
            }
            
            if trans_type == "income":
                incomes.append(transaction)
            else:
                expenses.append(transaction)
        
        # Tính tổng
        total_incomes = sum(t["amount"] for t in incomes)
        total_expenses = sum(t["amount"] for t in expenses)
        
        return {
            "transactions": {
                "incomes": incomes,
                "expenses": expenses
            },
            "total_amount": {
                "incomes": total_incomes,
                "expenses": total_expenses
            }
        }