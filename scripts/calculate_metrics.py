"""Recalcula metricas tras completar manualmente la matriz de resultados."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evidence" / "resultados_pruebas.csv"
OUTPUT = ROOT / "evidence" / "metricas_finales.json"


def normalized(value: str) -> str:
    return value.strip().lower().replace("í", "i")


def main() -> None:
    if not RESULTS.exists():
        raise SystemExit("Primero ejecuta: python scripts/run_evaluation.py")

    with RESULTS.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))

    executed = [
        row for row in rows if normalized(row.get("cumple", "")) in {"si", "no"}
    ]
    passed = [row for row in executed if normalized(row["cumple"]) == "si"]
    classified = [
        row
        for row in executed
        if row.get("categoria_obtenida") and row.get("prioridad_obtenida")
    ]
    correct = [
        row
        for row in classified
        if row["categoria_obtenida"] == row["categoria_esperada"]
        and row["prioridad_obtenida"] == row["prioridad_esperada"]
    ]
    times = []
    for row in executed:
        try:
            times.append(float(row.get("tiempo_segundos", "")))
        except ValueError:
            pass

    metrics = {
        "pruebas_ejecutadas": len(executed),
        "pruebas_satisfactorias": len(passed),
        "tasa_satisfactorias_porcentaje": round(
            len(passed) / len(executed) * 100, 2
        )
        if executed
        else 0,
        "clasificaciones_evaluadas": len(classified),
        "clasificaciones_correctas": len(correct),
        "exactitud_clasificacion_porcentaje": round(
            len(correct) / len(classified) * 100, 2
        )
        if classified
        else 0,
        "consultas_con_tiempo": len(times),
        "tiempo_promedio_respuesta_segundos": round(mean(times), 3) if times else 0,
    }
    OUTPUT.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"Guardado en: {OUTPUT}")


if __name__ == "__main__":
    main()

