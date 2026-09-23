"""Validacion y transcripcion de archivos de audio."""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from config import settings
from services.client import friendly_service_error, get_openai_client
from services.exceptions import SmartSupportError, ValidationError


ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a"}


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    filename: str
    model: str


def transcribe_uploaded_audio(uploaded_file) -> TranscriptionResult:
    if uploaded_file is None:
        raise ValidationError("Selecciona un archivo de audio.")

    filename = Path(uploaded_file.name).name
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValidationError("Formato no permitido. Usa MP3, WAV o M4A.")

    content = uploaded_file.getvalue()
    if not content:
        raise ValidationError("El archivo de audio esta vacio.")
    if len(content) > settings.max_audio_mb * 1024 * 1024:
        raise ValidationError(
            f"El audio supera el limite de {settings.max_audio_mb} MB."
        )

    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(content)
            temp_path = temp.name

        with open(temp_path, "rb") as audio:
            response = get_openai_client().audio.transcriptions.create(
                model=settings.transcription_model,
                file=audio,
                language="es",
            )
        text = (getattr(response, "text", "") or "").strip()
        if not text:
            raise RuntimeError("Transcripcion vacia")
        return TranscriptionResult(text=text, filename=filename, model=settings.transcription_model)
    except SmartSupportError:
        raise
    except Exception as error:
        raise friendly_service_error(error, "No se pudo transcribir el audio") from error
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)

