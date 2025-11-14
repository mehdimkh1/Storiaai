"""Application configuration helpers."""
from functools import lru_cache
from typing import Dict, Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4.1-mini")

    llm_provider: Literal["openai", "ollama", "huggingface"] = Field(default="huggingface")
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_story_model: str = Field(default="mistral")
    ollama_summary_model: str = Field(default="mistral")

    huggingface_api_key: Optional[str] = Field(default=None)
    huggingface_base_url: str = Field(default="https://api-inference.huggingface.co")
    huggingface_story_model: str = Field(default="microsoft/DialoGPT-large")
    huggingface_summary_model: str = Field(default="microsoft/DialoGPT-large")
    huggingface_tts_model: Optional[str] = Field(default="suno/bark-small")

    elevenlabs_api_key: Optional[str] = Field(default=None)
    elevenlabs_voice_id: Optional[str] = Field(default=None)

    murf_api_key: Optional[str] = Field(default=None)
    murf_voice_id: Optional[str] = Field(default=None)

    database_url: str = Field(default="sqlite:///./storiaai.db")
    database_echo: bool = Field(default=False)

    max_free_stories_per_day: int = Field(default=3)
    allow_premium_override: bool = Field(default=True)

    banned_words: tuple[str, ...] = Field(
        default=(
            "morte",
            "sangue",
            "paura",
            "mostro",
            "arma",
            "violenza",
            "dead",
            "blood",
            "muerte",
            "sangre",
            "miedo",
            "mort",
            "sang",
            "peur",
            "موت",
            "دم",
            "خوف",
        ),
    )

    allowed_languages: tuple[str, ...] = Field(default=("ar", "en", "es", "fr", "it"))

    use_gtts: bool = Field(default=True)
    edge_tts_enabled: bool = Field(default=True)
    edge_tts_rate: str = Field(default="+0%")
    edge_tts_pitch: str = Field(default="+0Hz")
    edge_tts_voice_map: Dict[str, str] = Field(
        default_factory=lambda: {
            "ar": "ar-SA-HamedNeural",
            "en": "en-GB-LibbyNeural",
            "es": "es-ES-ElviraNeural",
            "fr": "fr-FR-DeniseNeural",
            "it": "it-IT-IsabellaNeural",
            "default": "en-US-JennyNeural",
        }
    )

    offline_mode: bool = Field(default=False)

    # Security settings
    jwt_secret_key: str = Field(default="your-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)

    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379")
    cache_ttl_seconds: int = Field(default=3600)

    # Logging
    log_level: str = Field(default="INFO")
    sentry_dsn: Optional[str] = Field(default=None)

    @property
    def use_stub_providers(self) -> bool:
        """Return True when AI providers should be stubbed out."""

        if self.offline_mode:
            return True

        llm_ready = False
        provider = self.llm_provider
        if provider == "openai":
            llm_ready = bool(self.openai_api_key)
        elif provider == "ollama":
            llm_ready = True
        elif provider == "huggingface":
            llm_ready = bool(self.huggingface_api_key)

        return not llm_ready


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance."""

    return Settings()
