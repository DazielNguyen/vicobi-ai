from pathlib import Path
from typing import Dict, Any
import google.generativeai as genai
from .config import Config
from ...schemas.base import VoiceTotalAmountSchema, VoiceTransactionsSchema, VoiceTransactionDetailSchema
import json
import re
import time

class GeminiVoiceExtractor:
    """Extract structured data from voice transcripts using Gemini API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self.prompt_template = self._load_prompt_template()
        self._initialize_model()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from extraction_voice_vi.txt"""
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "extraction_voice_vi.txt"
        try:
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception:
            pass
        return "Extract transaction data from this voice transcript and convert to JSON"
    
    def _initialize_model(self) -> None:
        """Initialize Gemini model with API key from config"""
        api_key = self.config.get('api.api_key')
        if not api_key:
            raise ValueError("Gemini API key not found in configuration")
        
        genai.configure(api_key=api_key)
        
        model_version = self.config.get('api.model_version', 'gemini-2.5-flash')
        self.model = genai.GenerativeModel(model_version)
    
    def extract_from_text(
        self,
        text: str,
        return_raw: bool = False
    ) -> Dict[str, Any]:
        """
        Xử lý văn bản trích xuất từ voice transcript và trả về dữ liệu có cấu trúc
        
        Args:
            text: Văn bản trích xuất từ voice transcript
            return_raw: Nếu True, trả về văn bản phản hồi thô thay vì JSON đã phân tích
            
        Returns:
            Dictionary chứa dữ liệu đã trích xuất hoặc phản hồi thô
        """
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        full_prompt = f"{self.prompt_template}\n\nTranscript:\n{text}"
        
        response = self.model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        tokens_used = 0
        if hasattr(response, 'usage_metadata'):
            tokens_used = getattr(response.usage_metadata, 'total_token_count', 0)
        
        if return_raw:
            return {"raw_response": response_text, "tokens_used": tokens_used}

        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        try:
            result = json.loads(response_text)
            
            if "total_amount" not in result:
                result["total_amount"] = {"incomes": 0.0, "expenses": 0.0}
            if "transactions" not in result:
                result["transactions"] = {"incomes": [], "expenses": []}
            if "money_type" not in result:
                result["money_type"] = "VND"
            
            result["tokens_used"] = tokens_used
                
            return result
        except json.JSONDecodeError as e:
            return {
                "total_amount": {"incomes": 0.0, "expenses": 0.0},
                "transactions": {"incomes": [], "expenses": []},
                "money_type": "VND",
                "tokens_used": tokens_used,
                "error": f"JSON decode error: {str(e)}",
                "raw_response": response_text
            }
    
    def extract_to_schema(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Extract structured data from voice transcript and convert to Pydantic schema
        
        Args:
            text: Voice transcript text to process
            
        Returns:
            Dictionary containing validated schema objects with metadata
        """
        start_time = time.time()
        
        json_result = self.extract_from_text(text, return_raw=False)
        
        try:
            total_amount_data = json_result.get('total_amount', {})
            total_amount = VoiceTotalAmountSchema(
                incomes=total_amount_data.get('incomes', 0.0),
                expenses=total_amount_data.get('expenses', 0.0)
            )
            
            transactions_data = json_result.get('transactions', {})
            
            incomes = []
            for income_data in transactions_data.get('incomes', []):
                income = VoiceTransactionDetailSchema(**income_data)
                incomes.append(income)
            
            expenses = []
            for expense_data in transactions_data.get('expenses', []):
                expense = VoiceTransactionDetailSchema(**expense_data)
                expenses.append(expense)
            
            transactions = VoiceTransactionsSchema(
                incomes=incomes,
                expenses=expenses
            )
        
            processing_time = time.time() - start_time
            
            return {
                'total_amount': total_amount,
                'transactions': transactions,
                'money_type': json_result.get('money_type', 'VND'),
                'processing_time': round(processing_time, 2),
                'tokens_used': json_result.get('tokens_used', 0)
            }
            
        except Exception as e:
            raise ValueError(f"Failed to convert JSON to schema: {str(e)}")
