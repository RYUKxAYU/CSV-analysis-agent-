from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/datalens"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Auth
    JWT_SECRET: str = "your-very-long-random-secret-key-here-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AI
    GROQ_API_KEY: str = ""
    
    # GCP Cloud Storage
    GCP_PROJECT_ID: str = ""
    GCS_BUCKET_NAME: str = ""
    GCP_KEY_FILE_PATH: str = "./gcp-key.json"
    GCP_SERVICE_ACCOUNT_JSON: str = ""
    
    # App
    MAX_FILE_SIZE_MB: int = 10
    CORS_ORIGINS: str = "http://localhost:3000,https://your-frontend.vercel.app"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()