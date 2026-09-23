"""Configuracion central de HM Smart Support."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _positive_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
        return value if value > 0 else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini").strip()
    transcription_model: str = os.getenv(
        "OPENAI_TRANSCRIPTION_MODEL", "whisper-1"
    ).strip()
    max_history_messages: int = _positive_int("MAX_HISTORY_MESSAGES", 12)
    max_audio_mb: int = _positive_int("MAX_AUDIO_MB", 25)


settings = Settings()

