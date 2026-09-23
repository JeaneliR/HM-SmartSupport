"""Ejecuta los casos de texto y deja los casos de audio para validacion manual."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from statistics import mean
from time import perf_counter


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.chat_service import generate_reply  # noqa: E402
from services.classifier_service import classify_query  # noqa: E402
from services.exceptions import SmartSupportError  # noqa: E402


def main() -> None:
    source = ROOT / "tests" / "casos_prueba.csv"
    output = ROOT / "evidence" / "resultados_pruebas.csv"
    metrics_path = ROOT / "evidence" / "metricas.json"

    with source.open(encoding="utf-8-sig", newline="") as stream:
        cases = list(csv.DictReader(stream))

    rows = []
    times = []
    correct = 0
    executed = 0
    passed = 0
    context_history: list[dict] = []

    for case in cases:
        row = dict(case)
        row.update(
            obtenido="",
            categoria_obtenida="",
            prioridad_obtenida="",
            tiempo_segundos="",
            cumple="Pendiente manual" if case["tipo"] == "audio" else "No",
            observaciones=(
                "Cargar el audio en Streamlit y registrar evidencia."
                if case["tipo"] == "audio"
                else ""
            ),
        )
        if case["tipo"] == "audio":
            rows.append(row)
            continue

        history = context_history if case["id"] == "CP08" else []
        try:
            started = perf_counter()
            chat = generate_reply(case["entrada"], history, "V3")
            classification = classify_query(case["entrada"], history)
            total_elapsed = round(perf_counter() - started, 3)
            category_ok = classification.categoria == case["categoria_esperada"]
            priority_ok = classification.prioridad == case["prioridad_esperada"]
            success = bool(chat.answer.strip()) and category_ok and priority_ok

            row.update(
                obtenido=chat.answer,
                categoria_obtenida=classification.categoria,
                prioridad_obtenida=classification.prioridad,
                tiempo_segundos=f"{total_elapsed:.3f}",
                cumple="Sí" if success else "No",
                observaciones="Revisar cualitativamente la respuesta antes de entregar.",
            )
            times.append(total_elapsed)
            correct += int(category_ok and priority_ok)
            executed += 1
            passed += int(success)

            if case["id"] == "CP07":
                context_history = [
                    {"role": "user", "content": case["entrada"]},
                    {"role": "assistant", "content": chat.answer},
                ]
        except SmartSupportError as error:
            row["observaciones"] = str(error)
            executed += 1

        rows.append(row)

    fieldnames = list(rows[0].keys())
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    metrics = {
        "pruebas_totales_planificadas": len(cases),
        "pruebas_automaticas_ejecutadas": executed,
        "pruebas_de_audio_pendientes": sum(c["tipo"] == "audio" for c in cases),
        "tasa_satisfactorias_porcentaje": round((passed / executed * 100), 2) if executed else 0,
        "exactitud_clasificacion_porcentaje": round((correct / executed * 100), 2) if executed else 0,
        "tiempo_promedio_respuesta_segundos": round(mean(times), 3) if times else 0,
        "nota": "Completar manualmente los audios y recalcular las metricas finales antes de entregar.",
    }
    metrics_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Resultados: {output}")
    print(f"Metricas: {metrics_path}")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
