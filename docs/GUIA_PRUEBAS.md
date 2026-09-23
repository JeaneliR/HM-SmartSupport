# Guía de pruebas y evidencias

La matriz base contiene 14 casos: 11 de texto y 3 de audio. Así se supera el
mínimo de 12 y se obtienen al menos 10 tiempos de consultas de texto.

## Audios que debe grabar el equipo

Graba audios breves, sin datos personales, y guárdalos en `tests/assets`:

1. `consulta_mantenimiento.wav`: “¿Cómo debo limpiar mi máquina de coser al
   terminar la jornada?”
2. `consulta_repuesto.m4a`: “Necesito una cuchilla para mi remalladora, pero no
   sé cuál es compatible.”
3. `consulta_falla.mp3`: “Mi bordadora hace un ruido fuerte y se detiene cuando
   empiezo a usarla.”

## Evidencia recomendada

- Captura del nombre del archivo cargado.
- Captura de la transcripción visible.
- Captura después de pulsar “Usar transcripción como consulta”.
- Respuesta, categoría, prioridad y tiempo.
- Para CP07 y CP08, muestra ambas preguntas en el mismo historial.
- Para CP13, muestra la advertencia de seguridad y prioridad Crítica.

No marques “Sí” por adelantado. Registra lo que realmente produjo la ejecución.

