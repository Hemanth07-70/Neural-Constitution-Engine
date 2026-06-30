from pydantic_settings import BaseSettings


class ProviderSettings(BaseSettings):
    """Configuration for AI Providers."""

    # Can be overridden via DB or environment
    default_provider: str = "openai"
    default_model: str = "gpt-4o"

    provider_timeout_seconds: int = 30
    provider_max_retries: int = 3

    # API Keys are typically fetched securely. For the demo:
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    ollama_base_url: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        extra = "ignore"


provider_settings = ProviderSettings()
