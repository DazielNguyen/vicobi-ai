from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str | None = "VicobiAI"
    API_PREFIX: str | None = "/api/v1"
    VERSION: str | None = "1.0.0"

    MONGO_INITDB_ROOT_USERNAME: str 
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_DATABASE: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()