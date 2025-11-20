from pathlib import Path
from typing import Dict, Any, Union, TYPE_CHECKING, Optional
from PIL import Image
import google.generativeai as genai  # type: ignore
from .config import Config
from ...schemas.base import BillTotalAmountSchema, BillTransactionsSchema, BillTransactionDetailSchema

class GeminiInvoiceExtractor:
    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self.prompt_template = self._load_prompt_template()
        self._initialize_model()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from extraction_bill_vi.txt"""
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "extraction_bill_vi.txt"
        try:
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception:
            pass
        # Fallback default prompt
        return "Extract invoice data to JSON"
    
    def _initialize_model(self) -> None:
        api_key = self.config.get('api.api_key')
        if not api_key:
            raise ValueError("Gemini API key not found in configuration")
        
        genai.configure(api_key=api_key)  # type: ignore
        
        model_version = self.config.get('api.model_version', 'gemini-1.5-flash')
        self.model = genai.GenerativeModel(model_version)  # type: ignore
    
    def extract(
        self,
        image_path: Union[str, Path],
        return_raw: bool = False
    ) -> Dict[str, Any]:
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = Image.open(image_path)
        
        response = self.model.generate_content([self.prompt_template, image])
        
        if return_raw:
            return {"raw_response": response.text}
        
        import json
        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            return {"extracted_text": response.text}
    
    def extract_to_schema(
        self,
        image_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Extract structured data from invoice image and convert to Pydantic schema
        
        Args:
            image_path: Path to invoice image file
            
        Returns:
            Dictionary containing validated schema objects
        """
        # First extract JSON from Gemini
        json_result = self.extract(image_path, return_raw=False)
        
        # Convert JSON to Pydantic schemas
        try:
            # Parse total_amount
            total_amount_data = json_result.get('total_amount', {})
            total_amount = BillTotalAmountSchema(
                expenses=total_amount_data.get('expenses', 0.0)
            )
            
            # Parse transactions
            transactions_data = json_result.get('transactions', {})
            
            # Parse expenses
            expenses = []
            for expense_data in transactions_data.get('expenses', []):
                expense = BillTransactionDetailSchema(**expense_data)
                expenses.append(expense)
            
            transactions = BillTransactionsSchema(
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
