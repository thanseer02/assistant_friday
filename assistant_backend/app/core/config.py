from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Local Assistant Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # SQLite Database Config
    DATABASE_URL: str = "sqlite:///./assistant.db"
    
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
