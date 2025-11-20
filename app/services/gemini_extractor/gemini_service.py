from pathlib import Path
from typing import Dict, Any, Optional, Union
from PIL import Image

from .config import Config, load_config
from .bill import GeminiInvoiceExtractor
from .voice import GeminiVoiceExtractor

class GeminiService:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        self.extractor: Optional[GeminiInvoiceExtractor] = None
        self.voice_extractor: Optional[GeminiVoiceExtractor] = None
        self._initialize_extractor()
    
    def _initialize_extractor(self) -> None:
        try:
            self.extractor = GeminiInvoiceExtractor(self.config)
            self.voice_extractor = GeminiVoiceExtractor(self.config)
        except Exception as e:
            self.extractor = None
            self.voice_extractor = None
            raise
    
    def is_ready(self) -> bool:
        return self.extractor is not None and self.voice_extractor is not None
    
    def get_model_version(self) -> Optional[str]:
        if self.config:
            return self.config.get('api.model_version')
        return None
    
    def extract_from_image(
        self,
        image_path: Union[str, Path],
        return_raw: bool = False
    ) -> Dict[str, Any]:
        if not self.is_ready() or self.extractor is None:
            raise RuntimeError("Gemini Service is not initialized")
        
        try:
            result = self.extractor.extract(
                image_path=image_path,
                return_raw=return_raw
            )
            return result
        except Exception as e:
            raise
    
    def extract_from_image_to_schema(
        self,
        image_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """Extract from image and convert to Pydantic schema"""
        if not self.is_ready() or self.extractor is None:
            raise RuntimeError("Gemini Service is not initialized")
        
        try:
            result = self.extractor.extract_to_schema(image_path=image_path)
            return result
        except Exception as e:
            raise
    
    def extract_from_text(
        self,
        text: str,
        return_raw: bool = False
    ) -> Dict[str, Any]:
        """Extract structured data from voice transcript text"""
        if not self.is_ready() or self.voice_extractor is None:
            raise RuntimeError("Gemini Service is not initialized")
        
        try:
            result = self.voice_extractor.extract_from_text(
                text=text,
                return_raw=return_raw
            )
            return result
        except Exception as e:
            raise
    
    def extract_from_text_to_schema(
        self,
        text: str
    ) -> Dict[str, Any]:
        """Extract from text and convert to Pydantic schema"""
        if not self.is_ready() or self.voice_extractor is None:
            raise RuntimeError("Gemini Service is not initialized")
        
        try:
            result = self.voice_extractor.extract_to_schema(text=text)
            return result
        except Exception as e:
            raise
    
    def extract_voice_data(self, text: str) -> Dict[str, Any]:
        """
        Extract voice transaction data from transcription text using Gemini
        
        Args:
            text: Transcribed text from voice input
            
        Returns:
            Dictionary containing:
            - total_amount: {"incomes": float, "expenses": float}
            - transactions: {"incomes": [dict], "expenses": [dict]}
            - money_type: str (default "VND")
        """
        if not self.is_ready() or self.voice_extractor is None:
            raise RuntimeError("Gemini Service is not initialized")
        
        try:
            # Extract JSON from Gemini using the voice extractor
            result = self.voice_extractor.extract_from_text(text=text, return_raw=False)
            
            # Post-process to ensure all required fields exist
            transactions = result.get("transactions", {})
            
            # Process incomes
            incomes = []
            for item in transactions.get("incomes", []):
                processed_item = self._process_transaction_item(item, "income")
                incomes.append(processed_item)
            
            # Process expenses
            expenses = []
            for item in transactions.get("expenses", []):
                processed_item = self._process_transaction_item(item, "expense")
                expenses.append(processed_item)
            
            # Convert to expected format
            return {
                "total_amount": {
                    "incomes": result.get("total_amount", {}).get("incomes", 0.0),
                    "expenses": result.get("total_amount", {}).get("expenses", 0.0)
                },
                "transactions": {
                    "incomes": incomes,
                    "expenses": expenses
                },
                "money_type": result.get("money_type", "VND")
            }
        except Exception as e:
            raise Exception(f"Lỗi khi extract voice data với Gemini: {str(e)}")
    
    def _process_transaction_item(self, item: Dict[str, Any], transaction_type: str) -> Dict[str, Any]:
        """
        Process a single transaction item to ensure all required fields exist
        
        Args:
            item: Transaction item from Gemini
            transaction_type: "income" or "expense"
            
        Returns:
            Processed transaction item with all required fields
        """
        # Ensure transaction_type exists
        if "transaction_type" not in item:
            item["transaction_type"] = transaction_type
        
        # Ensure amount_string exists
        if "amount_string" not in item:
            amount = item.get("amount", 0)
            item["amount_string"] = self._format_amount_string(amount)
        
        # Ensure quantity exists
        if "quantity" not in item:
            item["quantity"] = 1.0
        
        # Build description from category if description is missing
        if "description" not in item or not item["description"]:
            category = item.get("category", "Giao dịch")
            item["description"] = category
        
        return item
    
    def _format_amount_string(self, amount: float) -> str:
        """
        Format amount as Vietnamese string
        
        Args:
            amount: Numeric amount
            
        Returns:
            Formatted string (e.g., "50 nghìn", "2 triệu")
        """
        if amount >= 1_000_000:
            if amount % 1_000_000 == 0:
                return f"{int(amount / 1_000_000)} triệu"
            else:
                return f"{amount / 1_000_000:.1f} triệu"
        elif amount >= 1_000:
            if amount % 1_000 == 0:
                return f"{int(amount / 1_000)} nghìn"
            else:
                return f"{amount / 1_000:.1f} nghìn"
        else:
            return f"{int(amount)} đồng"
    
    def validate_config(self) -> Dict[str, Any]:
        return {
            "config_loaded": self.config is not None,
            "extractor_initialized": self.is_ready(),
            "model_version": self.get_model_version(),
            "api_key_present": self.config.get('api.api_key') is not None if self.config else False
        }


_gemini_service_instance: Optional[GeminiService] = None


def get_gemini_service(config: Optional[Config] = None) -> GeminiService:
    """
    Get or create the singleton Gemini Service instance
    
    Args:
        config: Optional Config object for initialization
        
    Returns:
        GeminiService instance
    """
    global _gemini_service_instance
    
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService(config)
    
    return _gemini_service_instance


def reset_gemini_service() -> None:
    """Reset the singleton service instance (useful for testing)"""
    global _gemini_service_instance
    _gemini_service_instance = None
