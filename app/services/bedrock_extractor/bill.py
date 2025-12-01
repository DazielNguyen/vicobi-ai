import time
import json
import re
import boto3
from pathlib import Path
from typing import Dict, Any
from botocore.exceptions import ClientError
from .config import Config
from ...schemas.base import BillTotalAmountSchema, BillTransactionsSchema, BillTransactionDetailSchema

class BedrockBillExtractor:
    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self.model_id = None
        self.prompt_template = self._load_prompt_template()
        self._initialize_client()
    
    def _load_prompt_template(self) -> str:
        """Tải mẫu prompt từ extraction_bill_vi.txt"""
        # Điều chỉnh đường dẫn tùy theo cấu trúc project của bạn
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "extraction_bill_en.txt"
        print(f"Loading prompt template from: {prompt_path}")
        try:
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception:
            pass
        return "Extract invoice data to JSON"
    
    def _initialize_client(self) -> None:
        region = self.config.get('aws.region', 'ap-southeast-1')
        self.model_id = self.config.get('aws.model_id', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        
        # Boto3 sẽ tự tìm credentials từ env var hoặc IAM Role
        self.client = boto3.client(service_name='bedrock-runtime', region_name=region)
        
    def _ocr_list_to_string(self, ocr_output: list) -> str:
        if not ocr_output:
            return ""
        lines = [entry["text"] for entry in ocr_output if isinstance(entry, dict) and "text" in entry]
        return "\n".join(lines)
    
    def extract_from_text(self, text: str | list, return_raw: bool = False) -> Dict[str, Any]:
        if self.client is None:
            raise RuntimeError("Bedrock Client not initialized")

        if isinstance(text, list):
            text = self._ocr_list_to_string(text)

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        full_prompt = f"{self.prompt_template}\n\nTranscript:\n{text}"
        
        # Cấu trúc body cho model Claude 3
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": self.config.get('aws.generation.temperature', 0.1),
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        })

        try:
            response = self.client.invoke_model(
                body=body,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            
            response_body = json.loads(response.get('body').read())
            
            # Lấy text từ response của Claude
            response_text = response_body.get('content')[0].get('text').strip()
            
            # Tính toán tokens (nếu response trả về)
            usage = response_body.get('usage', {})
            tokens_used = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            
            if return_raw:
                return {"raw_response": response_text, "tokens_used": tokens_used}

            # Parse JSON từ text trả về
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            
            result = json.loads(response_text)
            result.setdefault("total_amount", {"expenses": 0.0})
            result.setdefault("transactions", {"expenses": []})
            result.setdefault("money_type", "VND")
            result["tokens_used"] = tokens_used
            return result

        except (ClientError, json.JSONDecodeError) as e:
            return {
                "total_amount": {"expenses": 0.0},
                "transactions": {"expenses": []},
                "money_type": "VND",
                "tokens_used": 0,
                "error": str(e),
                "raw_response": str(e)
            }
    
    def extract_to_schema(self, text: str | list) -> Dict[str, Any]:
        """Convert output thành Schema chuẩn cho Bill Response"""
        if isinstance(text, list):
            text = self._ocr_list_to_string(text)

        start_time = time.time()
        json_result = self.extract_from_text(text, return_raw=False)
        
        try:
            total_amount_data = json_result.get('total_amount', {})
            total_amount = BillTotalAmountSchema(
                expenses=total_amount_data.get('expenses', 0.0)
            )
            
            transactions_data = json_result.get('transactions', {})
            expenses = [
                BillTransactionDetailSchema(**expense_data)
                for expense_data in transactions_data.get('expenses', [])
            ]
            
            transactions = BillTransactionsSchema(expenses=expenses)
        
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