import json
import re
import time
import boto3
from pathlib import Path
from typing import Dict, Any
from botocore.exceptions import ClientError
from .config import Config
from ...schemas.base import VoiceTotalAmountSchema, VoiceTransactionsSchema, VoiceTransactionDetailSchema

class BedrockVoiceExtractor:
    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self.model_id = None
        self.prompt_template = self._load_prompt_template()
        self._initialize_client()
    
    def _load_prompt_template(self) -> str:
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "extraction_voice_en.txt"
        try:
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception:
            pass
        return "Extract transaction data from this voice transcript and convert to JSON"
    
    def _initialize_client(self) -> None:
        region = self.config.get('aws.region', 'ap-southeast-1')
        self.model_id = self.config.get('aws.model_id', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        self.client = boto3.client(service_name='bedrock-runtime', region_name=region)
    
    def extract_from_text(self, text: str, return_raw: bool = False) -> Dict[str, Any]:
        if self.client is None:
            raise RuntimeError("Bedrock Client not initialized")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        full_prompt = f"{self.prompt_template}\n\nTranscript:\n{text}"
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": self.config.get('aws.generation.temperature', 0.1),
            "messages": [{"role": "user", "content": full_prompt}]
        })
        
        tokens_used = 0
        response_text = ""

        try:
            response = self.client.invoke_model(
                body=body,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            
            response_body = json.loads(response.get('body').read())
            response_text = response_body.get('content')[0].get('text').strip()
            usage = response_body.get('usage', {})
            tokens_used = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            
            if return_raw:
                return {"raw_response": response_text, "tokens_used": tokens_used}

            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            
            result = json.loads(response_text)
            
            if "total_amount" not in result:
                result["total_amount"] = {"incomes": 0.0, "expenses": 0.0}
            if "transactions" not in result:
                result["transactions"] = {"incomes": [], "expenses": []}
            if "money_type" not in result:
                result["money_type"] = "VND"
            
            result["tokens_used"] = tokens_used
            return result

        except (ClientError, json.JSONDecodeError) as e:
            return {
                "total_amount": {"incomes": 0.0, "expenses": 0.0},
                "transactions": {"incomes": [], "expenses": []},
                "money_type": "VND",
                "tokens_used": tokens_used,
                "error": str(e),
                "raw_response": response_text
            }
    
    def extract_to_schema(self, text: str) -> Dict[str, Any]:
        """Convert extraction output to standard schema"""
        start_time = time.time()
        json_result = self.extract_from_text(text, return_raw=False)
        
        try:
            total_amount_data = json_result.get('total_amount', {})
            total_amount = VoiceTotalAmountSchema(
                incomes=total_amount_data.get('incomes', 0.0),
                expenses=total_amount_data.get('expenses', 0.0)
            )
            
            transactions_data = json_result.get('transactions', {})
            
            incomes = [VoiceTransactionDetailSchema(**item) for item in transactions_data.get('incomes', [])]
            expenses = [VoiceTransactionDetailSchema(**item) for item in transactions_data.get('expenses', [])]
            
            transactions = VoiceTransactionsSchema(incomes=incomes, expenses=expenses)
        
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