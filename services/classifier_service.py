"""Clasificacion de categoria y prioridad con salida estructurada."""

from __future__ import annotations

import json
import unicodedata
from dataclasses import asdict, dataclass, replace
from typing import Iterable

from config import settings
from services.client import get_openai_client
from services.exceptions import SmartSupportError


CATEGORIES = (
    "Información",
    "Configuración",
    "Mantenimiento",
    "Garantía",
    "Repuesto",
    "Falla",
    "Servicio técnico",
    "Otros",
)
PRIORITIES = ("Baja", "Media", "Alta", "Crítica")


@dataclass(frozen=True)
class QueryClassification:
    categoria: str
    prioridad: str
    equipo: str
    problema: str
    requiere_atencion_tecnica: bool
    recomendacion: str
    fuente: str = "IA"

    def to_dict(self) -> dict:
        return asdict(self)


CLASSIFIER_PROMPT = """
Clasifica consultas de postventa de Hilos y Maquinas S.A.C.

Categorias permitidas: Información, Configuración, Mantenimiento, Garantía,
Repuesto, Falla, Servicio técnico, Otros.
Prioridades permitidas: Baja, Media, Alta, Crítica.

Criterios de prioridad:
- Crítica: humo, fuego, olor a quemado, chispas, descarga eléctrica o
  sobrecalentamiento; existe riesgo para la persona o el equipo.
- Alta: equipo inoperativo, atasco persistente, ruido fuerte/anormal continuo,
  fuga o falla que requiere revisión pronta.
- Media: configuración o problema operativo sin riesgo inmediato.
- Baja: información general, mantenimiento preventivo, repuesto o garantía sin
  urgencia manifiesta.

Devuelve SOLO un objeto JSON valido con estas claves exactas:
categoria, prioridad, equipo, problema, requiere_atencion_tecnica, recomendacion.
No agregues Markdown. No inventes marca ni modelo. Usa "no identificado" cuando
falte el equipo. Considera el contexto si el mensaje es de seguimiento.
""".strip()


def _plain(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _normalize_choice(value: object, allowed: tuple[str, ...], default: str) -> str:
    candidate = _plain(str(value).strip())
    for option in allowed:
        if candidate == _plain(option):
            return option
    return default


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return _plain(str(value)) in {"true", "verdadero", "si", "1"}


def parse_classification(payload: str | dict, source: str = "IA") -> QueryClassification:
    data = json.loads(payload) if isinstance(payload, str) else payload
    if not isinstance(data, dict):
        raise ValueError("La clasificacion no es un objeto JSON")

    return QueryClassification(
        categoria=_normalize_choice(data.get("categoria"), CATEGORIES, "Otros"),
        prioridad=_normalize_choice(data.get("prioridad"), PRIORITIES, "Media"),
        equipo=str(data.get("equipo") or "no identificado").strip()[:120],
        problema=str(data.get("problema") or "consulta no especificada").strip()[:300],
        requiere_atencion_tecnica=_as_bool(data.get("requiere_atencion_tecnica", False)),
        recomendacion=str(data.get("recomendacion") or "Solicitar mas informacion.").strip()[:400],
        fuente=source,
    )


def fallback_classification(query: str) -> QueryClassification:
    text = _plain(query)
    critical_words = ("humo", "quemado", "chisp", "descarga", "fuego", "sobrecalent")
    high_words = (
        "no enciende",
        "atasc",
        "trabada",
        "ruido",
        "suena raro",
        "fuga",
        "se rompio",
    )

    if any(word in text for word in critical_words):
        category, priority, technical = "Falla", "Crítica", True
        recommendation = "Detener el uso y solicitar evaluacion tecnica urgente."
    else:
        if "garantia" in text:
            category = "Garantía"
        elif any(word in text for word in ("repuesto", "aguja", "correa", "cuchilla", "pieza")):
            category = "Repuesto"
        elif any(word in text for word in ("mantenimiento", "limpiar", "lubric", "aceite")):
            category = "Mantenimiento"
        elif any(word in text for word in ("configur", "ajust", "tension", "programar")):
            category = "Configuración"
        elif any(word in text for word in ("tecnico", "visita", "reparacion")):
            category = "Servicio técnico"
        elif any(word in text for word in ("error", "falla", "no cose", "rompe el hilo", "ruido")):
            category = "Falla"
        elif any(word in text for word in ("maquina", "remalladora", "bordadora", "coser")):
            category = "Información"
        else:
            category = "Otros"

        urgent = any(word in text for word in high_words)
        priority = "Alta" if urgent else (
            "Media" if category in {"Falla", "Configuración", "Servicio técnico"} else "Baja"
        )
        technical = urgent or category == "Servicio técnico"
        recommendation = (
            "Solicitar revision tecnica."
            if technical
            else "Brindar orientacion y confirmar los datos del equipo."
        )

    equipment = "no identificado"
    for option in ("remalladora", "bordadora", "maquina de coser"):
        if option in text:
            equipment = option
            break

    return QueryClassification(
        categoria=category,
        prioridad=priority,
        equipo=equipment,
        problema=query.strip()[:300] or "consulta no especificada",
        requiere_atencion_tecnica=technical,
        recomendacion=recommendation,
        fuente="Reglas locales de respaldo",
    )

def apply_business_rules(
    query: str,
    classification: QueryClassification,
) -> QueryClassification:
    """Aplica criterios empresariales en casos inequívocos."""

    text = _plain(query)

    critical_words = (
        "humo",
        "quemado",
        "chisp",
        "descarga electrica",
        "fuego",
        "sobrecalent",
    )

    failure_words = (
        "no enciende",
        "atasc",
        "trabada",
        "ruido",
        "suena raro",
        "sonido raro",
        "fuga",
        "se rompio",
    )

    spare_part_words = (
        "repuesto",
        "aguja",
        "correa",
        "cuchilla",
        "pieza",
        "prensatela",
        "bobina",
    )

    configuration_words = (
        "configur",
        "ajust",
        "tension",
        "programar",
        "calibr",
    )

    updates: dict[str, object] = {}

    if any(word in text for word in critical_words):
        updates.update(
            categoria="Falla",
            prioridad="Crítica",
            requiere_atencion_tecnica=True,
            recomendacion=(
                "Detener el uso, desconectar el equipo si es seguro "
                "y solicitar evaluación técnica urgente."
            ),
        )

    elif any(word in text for word in failure_words):
        updates.update(
            categoria="Falla",
            prioridad="Alta",
            requiere_atencion_tecnica=True,
        )

    elif any(word in text for word in spare_part_words):
        updates["categoria"] = "Repuesto"

        if classification.prioridad not in {"Alta", "Crítica"}:
            updates["prioridad"] = "Baja"

    elif any(word in text for word in configuration_words):
        updates["categoria"] = "Configuración"

        if classification.prioridad == "Baja":
            updates["prioridad"] = "Media"

    if not updates:
        return classification

    updates["fuente"] = "IA + reglas de negocio"

    return replace(
        classification,
        **updates,
    )


def classify_query(query: str, history: Iterable[dict] = ()) -> QueryClassification:
    context = []
    for item in list(history)[-6:]:
        role = item.get("role")
        content = str(item.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            context.append({"role": role, "content": content[:1500]})

    user_payload = json.dumps(
        {"historial_reciente": context, "consulta_actual": query},
        ensure_ascii=False,
    )
    try:
        response = get_openai_client().chat.completions.create(
            model=settings.chat_model,
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user", "content": user_payload},
            ],
            temperature=0,
            response_format={"type": "json_object"},
            max_tokens=300,
        )
        classification = parse_classification(
            response.choices[0].message.content or "{}"
        )

        return apply_business_rules(
            query,
            classification,
        )
    except Exception:
        # La respuesta principal no se pierde si falla la segunda llamada.
        return fallback_classification(query)
