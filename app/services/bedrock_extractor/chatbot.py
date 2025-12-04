import json
import boto3
from pathlib import Path
from botocore.exceptions import ClientError
from .config import Config

class BedrockChatExtractor:
    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self.model_id = None
        self.prompt_template = self._load_prompt_template()
        self._initialize_client()

    def _load_prompt_template(self) -> str:
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "chat_system_prompt.txt"
        try:
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception:
            pass
        return """Bạn là trợ lý AI hữu ích. 
Dựa vào thông tin được cung cấp trong phần <context>, hãy trả lời câu hỏi của người dùng.
Nếu thông tin không có trong context, hãy nói là không biết."""

    def _initialize_client(self) -> None:
        region = self.config.get('aws.region', 'ap-southeast-1')
        self.model_id = self.config.get('aws.model_id', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        self.client = boto3.client(service_name='bedrock-runtime', region_name=region)

    def generate_response(self, context: str, question: str) -> str:
        if self.client is None:
            raise RuntimeError("Bedrock Client not initialized")

        system_prompt = self.prompt_template
        
        user_message = f"""<context>
{context}
</context>

{question}"""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "temperature": self.config.get('aws.generation.temperature', 0.3),
            "system": system_prompt,  # Sử dụng system parameter riêng
            "messages": [
                {
                    "role": "user",
                    "content": user_message
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
            response_text = response_body.get('content')[0].get('text').strip()
            
            return response_text

        except (ClientError, Exception) as e:
            return f"Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu: {str(e)}"