"""Generacion de respuestas con historial conversacional."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

from config import settings
from prompts.system_prompt import get_system_prompt
from services.client import friendly_service_error, get_openai_client
from services.exceptions import SmartSupportError, ValidationError


@dataclass(frozen=True)
class ChatResult:
    answer: str
    elapsed_seconds: float
    model: str


def _clean_history(history: Iterable[dict]) -> list[dict[str, str]]:
    cleaned: list[dict[str, str]] = []
    for item in list(history)[-settings.max_history_messages :]:
        role = item.get("role")
        content = str(item.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            cleaned.append({"role": role, "content": content[:6000]})
    return cleaned


def generate_reply(
    user_message: str,
    history: Iterable[dict],
    prompt_version: str = "V3",
) -> ChatResult:
    query = user_message.strip()
    if not query:
        raise ValidationError("Escribe una consulta antes de enviarla.")
    if len(query) > 6000:
        raise ValidationError("La consulta es demasiado extensa (maximo 6000 caracteres).")

    messages = [
        {"role": "system", "content": get_system_prompt(prompt_version)},
        *_clean_history(history),
        {"role": "user", "content": query},
    ]

    started = perf_counter()
    try:
        response = get_openai_client().chat.completions.create(
            model=settings.chat_model,
            messages=messages,
            temperature=0.2,
            max_tokens=700,
        )
        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            raise RuntimeError("Respuesta vacia")
    except SmartSupportError:
        raise
    except Exception as error:
        raise friendly_service_error(error, "No se pudo generar la respuesta") from error

    return ChatResult(
        answer=answer,
        elapsed_seconds=round(perf_counter() - started, 3),
        model=settings.chat_model,
    )

