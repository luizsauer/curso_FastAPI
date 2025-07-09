# fast_zero\settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the FastAPI application.
    This class uses Pydantic to manage configuration settings.
    """

    model_config = SettingsConfigDict(
        env_file='.env',  # Load environment variables from a .env file
        env_file_encoding='utf-8',  # Encoding for the .env file
        case_sensitive=True,
        extra='ignore',  # Ignore extra fields not defined in the model
    )  # Environment variable names are case-sensitive

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
