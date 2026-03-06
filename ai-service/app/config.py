from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    huggingface_api_token: str = ""
    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql://coldcase:coldcase_dev@localhost:5432/coldcase"
    app_name: str = "ColdCase AI Service"

    class Config:
        env_file = ".env"


settings = Settings()
