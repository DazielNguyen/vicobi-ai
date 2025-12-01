from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="VicobiAI")
    API_PREFIX: str = Field(default="/api/v1/ai")
    VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    
    MONGO_HOST: str = Field(default="localhost")
    MONGO_PORT: int = Field(default=27017)
    MONGO_INITDB_ROOT_USERNAME: str = Field(default="mongo")
    MONGO_INITDB_ROOT_PASSWORD: str = Field(default="12345")
    MONGO_INITDB_DATABASE: str = Field(default="VicobiMongoDB")
    
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL_VERSION: str = Field(default="gemini-2.5-flash")
    GEMINI_TIMEOUT: int = Field(default=30)
    GEMINI_TEMPERATURE: float = Field(default=0.1)
    GEMINI_MAX_RETRIES: int = Field(default=3)

    AWS_REGION: str = Field(default="ap-southeast-1")
    BEDROCK_MODEL_ID: str = Field(default="anthropic.claude-3-5-sonnet-20240620-v1:0")
    BEDROCK_TIMEOUT: int = Field(default=60)
    BEDROCK_TEMPERATURE: float = Field(default=0.0)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")

    USER_POOL_ID: str = Field(default="")
    APP_CLIENT_ID: str = Field(default="")
    REGION: str = Field(default="ap-southeast-1") 

    MODEL_BILL_FILE_NAME: str = Field(default="pytorch-bill_classifier.pth")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )
    
    @property
    def mongo_uri(self) -> str:
        return (
            f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}"
            f"@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_INITDB_DATABASE}?authSource=admin"
        )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


try:
    settings = Settings()
except Exception as e:
    print("❌ LỖI CONFIG: Thiếu biến môi trường bắt buộc!")
    raise e