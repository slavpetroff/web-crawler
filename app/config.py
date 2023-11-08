import os

from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    # Common settings, e.g., logging, that apply to all environments
    logging_level: str = "INFO"

    database_user: str
    database_pass: str
    database_host: str
    database_name: str
    database_schema: str = "public"

    rabbitmq_user: str
    rabbitmq_pass: str
    rabbitmq_host: str
    rabbitmq_port: int

    api_port: int = 8000
    api_host: str = "0.0.0.0"
    max_links_to_follow: int = 50

    @property
    def sqlalchemy_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.database_user}:{self.database_pass}@{self.database_host}/{self.database_name}"

    @property
    def sqlalchemy_sync_database_url(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_pass}@{self.database_host}/{self.database_name}"

    @property
    def broker_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_pass}@{self.rabbitmq_host}:{self.rabbitmq_port}/"


class DevelopmentSettings(CommonSettings):
    # Development environment specific settings
    class Config:
        env_file = "deployment/development/.env"
        env_file_encoding = "utf-8"


class ProductionSettings(CommonSettings):
    # Production environment specific settings
    class Config:
        env_file = "deployment/production/.env"
        env_file_encoding = "utf-8"


def get_settings() -> BaseSettings:
    # Determine the settings class to load based on the ENVIRONMENT env variable
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()  # default to development settings if not specified


# Use the get_settings function to load the appropriate settings based on the environment
settings = get_settings()
