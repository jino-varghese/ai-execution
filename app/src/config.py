"""
Configuration management for the application
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "AI Travel Itinerary Generator"
    environment: str = os.getenv("ENVIRONMENT", "dev")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database
    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database_name: str = os.getenv("DATABASE_NAME", "traveldb")
    database_user: str = os.getenv("DATABASE_USER", "postgres")
    database_password: str = os.getenv("DATABASE_PASSWORD", "")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

    # Redis
    redis_endpoint: str = os.getenv("REDIS_ENDPOINT", "localhost:6379")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    # OpenSearch
    opensearch_endpoint: str = os.getenv("OPENSEARCH_ENDPOINT", "http://localhost:9200")
    opensearch_user: str = os.getenv("OPENSEARCH_USER", "admin")
    opensearch_password: str = os.getenv("OPENSEARCH_PASSWORD", "")

    # S3
    s3_data_bucket: str = os.getenv("S3_DATA_BUCKET", "")
    s3_models_bucket: str = os.getenv("S3_MODELS_BUCKET", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    # SageMaker (Optional)
    sagemaker_endpoint: Optional[str] = os.getenv("SAGEMAKER_ENDPOINT")

    # Application Settings
    max_itinerary_days: int = 30
    default_budget: float = 1000.0
    cache_ttl: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
