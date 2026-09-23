# Guía rápida para Windows y PowerShell

## 1. Requisitos

- Python 3.10 o superior.
- Una clave de API de OpenAI con crédito disponible.
- Conexión a Internet.

## 2. Abrir el proyecto

Descomprime `HM-SmartSupport.zip`. En el Explorador de archivos, abre la
carpeta resultante, escribe `powershell` en la barra de dirección y presiona
Enter.

## 3. Crear y activar el entorno virtual

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, ejecuta una sola vez en esa ventana:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. Instalar dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configurar la API

```powershell
Copy-Item .env.example .env
notepad .env
```

Reemplaza únicamente `sk-reemplaza_con_tu_clave` por tu clave real. Guarda el
archivo. No muestres `.env` en el video ni lo subas a GitHub.

## 6. Ejecutar

```powershell
streamlit run app.py
```

Se abrirá `http://localhost:8501`. Para detener la aplicación, vuelve a
PowerShell y presiona `Ctrl + C`.

## 7. Verificar el código sin gastar API

```powershell
pytest -q
```

## 8. Ejecutar las pruebas reales

```powershell
python scripts\run_evaluation.py
```

Este comando sí consume API. Genera la matriz y las métricas en `evidence`.
Después debes ejecutar manualmente los casos de audio, completar sus filas y
recalcular:

```powershell
python scripts\calculate_metrics.py
```

## Errores frecuentes

- **Falta configurar OPENAI_API_KEY:** revisa que el archivo se llame `.env` y
  no `.env.txt`; reinicia Streamlit.
- **401 o clave inválida:** crea o copia nuevamente la clave.
- **429 o cuota:** revisa el saldo/límite de la cuenta API. ChatGPT Plus no
  incluye automáticamente crédito para la API.
- **No se reconoce streamlit:** activa `.venv` o usa
  `python -m streamlit run app.py`.

