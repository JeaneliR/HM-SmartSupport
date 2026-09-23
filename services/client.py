"""Creacion centralizada del cliente de OpenAI."""

from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from config import settings
from services.exceptions import ConfigurationError, ServiceError


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    if not settings.api_key or settings.api_key == "sk-reemplaza_con_tu_clave":
        raise ConfigurationError(
            "Falta configurar OPENAI_API_KEY. Copia .env.example como .env, "
            "coloca una clave valida y reinicia Streamlit."
        )
    return OpenAI(api_key=settings.api_key, timeout=60.0, max_retries=2)


def friendly_service_error(error: Exception, action: str) -> ServiceError:
    name = type(error).__name__.lower()
    message = str(error).lower()

    if "authentication" in name or "api key" in message or "401" in message:
        detail = "La clave de API no es valida o no tiene acceso al servicio."
    elif "ratelimit" in name or "quota" in message or "429" in message:
        detail = "Se alcanzo el limite o la cuota de la API. Intenta mas tarde."
    elif "timeout" in name:
        detail = "El servicio tardo demasiado en responder. Intenta nuevamente."
    elif "connection" in name:
        detail = "No se pudo conectar con la API. Revisa tu conexion a Internet."
    else:
        detail = "El servicio de IA no pudo completar la solicitud."

    return ServiceError(f"{action}: {detail}")

