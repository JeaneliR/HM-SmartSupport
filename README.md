# HM Smart Support

Prototipo académico de asistente inteligente multimodal para la postventa de
Hilos y Máquinas S.A.C. Cumple los requerimientos de la TA2 del curso
Herramientas de Desarrollo Profesional - TIC.

## Funciones implementadas

- Chat por texto con una API de IA.
- Historial visible y contexto con `st.session_state`.
- Prompt V1, V2 y V3 seleccionables para comparar su evolución.
- Audio MP3, WAV y M4A: carga, reproducción, transcripción editable y envío al chat.
- Clasificación estructurada por categoría y prioridad.
- Manejo de consultas desconocidas, fuera de dominio y situaciones críticas.
- Reinicio de conversación y mensajes de error comprensibles.
- API Key protegida mediante `.env`.
- 14 casos de prueba, cálculo de métricas y pruebas unitarias.

## Arquitectura

```text
USUARIO (texto/audio)
        ↓
STREAMLIT (app.py)
        ↓
SESSION STATE + PROMPT V1/V2/V3
        ↓
SERVICIOS (chat, audio, clasificación)
        ↓
OPENAI API
        ↓
RESPUESTA + CLASIFICACIÓN JSON
```

La interfaz permanece en `app.py`; la lógica se separa en `services`; los
prompts están en `prompts`; la información controlada del negocio, en `data`.

## Inicio rápido

### Windows / PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
streamlit run app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

En `.env`, reemplaza el valor de ejemplo de `OPENAI_API_KEY`. Una suscripción a
ChatGPT y el saldo de la API son servicios independientes.

## Pruebas

Pruebas unitarias sin consumo de API:

```bash
pytest -q
```

Evaluación funcional real (consume API):

```bash
python scripts/run_evaluation.py
```

La matriz resultante se guarda en `evidence/resultados_pruebas.csv`. Los tres
casos de audio se completan manualmente con audios reales. Luego:

```bash
python scripts/calculate_metrics.py
```

No se incluyen resultados inventados: el equipo debe ejecutar el proyecto,
conservar capturas y reportar las métricas efectivamente obtenidas.

## Categorías y prioridades

Categorías: Información, Configuración, Mantenimiento, Garantía, Repuesto,
Falla, Servicio técnico y Otros.

Prioridades: Baja, Media, Alta y Crítica. Humo, fuego, olor a quemado, chispas,
descarga eléctrica o sobrecalentamiento se tratan como situaciones críticas.

## Documentación incluida

- `docs/GUIA_RAPIDA_WINDOWS.md`: instalación paso a paso.
- `docs/GUIA_PRUEBAS.md`: preparación de audios y evidencias.
- `docs/COMPARACION_PROMPTS.md`: matriz V1/V2/V3.
- `docs/GUION_VIDEO.md`: estructura sugerida para la demostración.
- `docs/arquitectura.png`: diagrama para informe y presentación.

## Límites conocidos

- Requiere Internet, una clave válida y cuota de API.
- La base académica no contiene inventario, precios ni condiciones particulares
  de garantía; el asistente no debe inventarlos.
- La clasificación generada por IA debe validarse en pruebas. Existe un respaldo
  local por reglas si solo falla el formato de clasificación.
- No reemplaza una inspección técnica ni debe usarse para reparaciones peligrosas.

## Seguridad

Nunca subas `.env`, claves, datos sensibles de clientes ni audios reales con
información personal. El `.gitignore` ya excluye los secretos y resultados
locales. Antes del video, cierra cualquier archivo que muestre la clave.

