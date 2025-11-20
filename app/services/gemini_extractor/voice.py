from pathlib import Path
from typing import Dict, Any, Optional
import google.generativeai as genai  # type: ignore
from .config import Config
from ...schemas.base import VoiceTotalAmountSchema, VoiceTransactionsSchema, VoiceTransactionDetailSchema


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
        # Fallback default prompt
        return "Extract transaction data from this voice transcript and convert to JSON"
    
    def _initialize_model(self) -> None:
        """Initialize Gemini model with API key from config"""
        api_key = self.config.get('api.api_key')
        if not api_key:
            raise ValueError("Gemini API key not found in configuration")
        
        genai.configure(api_key=api_key)  # type: ignore
        
        model_version = self.config.get('api.model_version', 'gemini-1.5-flash')
        self.model = genai.GenerativeModel(model_version)  # type: ignore
    
    def extract_from_text(
        self,
        text: str,
        return_raw: bool = False
    ) -> Dict[str, Any]:
        """
        Extract structured data from voice transcript text
        
        Args:
            text: Voice transcript text to process
            return_raw: If True, return raw response text instead of parsed JSON
            
        Returns:
            Dictionary containing extracted data or raw response
        """
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Combine prompt template from file with text
        full_prompt = f"{self.prompt_template}\n\nTranscript:\n{text}"
        
        response = self.model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        if return_raw:
            return {"raw_response": response_text}
        
        import json
        import re
        
        # Try to extract JSON from response (in case there's markdown formatting)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        try:
            result = json.loads(response_text)
            
            # Validate and ensure structure exists
            if "total_amount" not in result:
                result["total_amount"] = {"incomes": 0.0, "expenses": 0.0}
            if "transactions" not in result:
                result["transactions"] = {"incomes": [], "expenses": []}
            if "money_type" not in result:
                result["money_type"] = "VND"
                
            return result
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return empty structure with error info
            return {
                "total_amount": {"incomes": 0.0, "expenses": 0.0},
                "transactions": {"incomes": [], "expenses": []},
                "money_type": "VND",
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
            Dictionary containing validated schema objects
        """
        # First extract JSON from Gemini
        json_result = self.extract_from_text(text, return_raw=False)
        
        # Convert JSON to Pydantic schemas
        try:
            # Parse total_amount
            total_amount_data = json_result.get('total_amount', {})
            total_amount = VoiceTotalAmountSchema(
                incomes=total_amount_data.get('incomes', 0.0),
                expenses=total_amount_data.get('expenses', 0.0)
            )
            
            # Parse transactions
            transactions_data = json_result.get('transactions', {})
            
            # Parse incomes
            incomes = []
            for income_data in transactions_data.get('incomes', []):
                income = VoiceTransactionDetailSchema(**income_data)
                incomes.append(income)
            
            # Parse expenses
            expenses = []
            for expense_data in transactions_data.get('expenses', []):
                expense = VoiceTransactionDetailSchema(**expense_data)
                expenses.append(expense)
            
            transactions = VoiceTransactionsSchema(
                incomes=incomes,
                expenses=expenses
            )
            
            # Return structured result
            return {
                'total_amount': total_amount,
                'transactions': transactions,
                'money_type': json_result.get('money_type', 'VND')
            }
            
        except Exception as e:
            raise ValueError(f"Failed to convert JSON to schema: {str(e)}")
