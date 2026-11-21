# Reglas de desarrollo

Estas reglas describen prácticas para implementar y mantener código en el monorepo. Cada una indica cuándo se aplica.

## 1. Mantener los cambios enfocados

**Alcance:** Siempre activa.

Resuelve la solicitud con el cambio más pequeño que la satisfaga. Conserva el comportamiento existente y evita refactorizaciones o modificaciones no relacionadas. No descartes cambios previos del desarrollador.

## 2. Validar y comunicar el resultado

**Alcance:** Siempre activa.

Después de modificar código, ejecuta las pruebas y comprobaciones pertinentes usando los comandos ya disponibles en el proyecto. Informa qué validaste y señala claramente cualquier prueba fallida o que no pudiste ejecutar; no afirmes que el cambio está verificado si no lo está.

## 3. Mantener las convenciones de Python

**Alcance:** Archivos que coincidan con `**/*.py`.

Respeta la versión mínima de Python declarada en `pyproject.toml` y el estilo del módulo existente. Prefiere tipos explícitos y manejo de errores concreto; evita capturas amplias y valores de respaldo que oculten fallos.

## 4. Revisar arquitectura solo cuando se solicite

**Alcance:** Solicitada por el agente.

Cuando el agente active esta regla para una tarea de diseño o refactorización, examina primero las responsabilidades, dependencias y patrones existentes en los componentes afectados. Propón o realiza únicamente cambios justificados por la tarea. No amplíes una corrección rutinaria para incluir una revisión arquitectónica no solicitada.