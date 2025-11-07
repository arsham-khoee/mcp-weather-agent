"""Manages environment variables, API keys, model parameters, and system-wide settings for the weather agent."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class ModelConfig:
    """Configuration for LLM model."""

    model_name: str = "openai/gpt-oss-20b"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class WeatherConfig:
    """Configuration for Weather API."""

    api_key: Optional[str] = None
    base_url: str = "https://api.weatherapi.com/v1"


class Settings:
    """Main configuration manager for the agent."""

    def __init__(self):
        """Initialize settings from environment variables."""
        # Load environment variables from .env file
        self.base_dir = Path(__file__).parent.parent
        load_dotenv(self.base_dir / ".env")

        # Initialize model configuration
        self.model_config = ModelConfig(
            model_name=os.getenv("MODEL_NAME", "openai/gpt-oss-20b"),
            base_url=os.getenv("MODEL_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("MODEL_API_KEY", None),
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "2048")),
        )

        # Weather API configuration
        self.weather_config = WeatherConfig(
            api_key=os.getenv("WEATHER_API_KEY"),
            base_url=os.getenv("WEATHER_BASE_URL", "https://api.weatherapi.com/v1")
        )

        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def validate_configuration(self) -> bool:
        """
        Validate all configuration settings.

        Returns:
            True if configuration is valid, False otherwise
        """
        required_keys = ["API_KEY", "BASE_URL"]
        missing_keys = [key for key in required_keys if not os.getenv(key)]

        if missing_keys:
            print(f"Missing required environment variables: {missing_keys}")
            return False

        return True


# Global settings instance
settings = Settings()