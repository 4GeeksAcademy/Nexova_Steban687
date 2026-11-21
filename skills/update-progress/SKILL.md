---
name: update-progress
description: Actualiza el progreso del proyecto a partir de evidencias verificables.
---

# Actualización del progreso

## Objetivo

Actualizar `memory-bank/progress.md` con el estado del proyecto respaldado por evidencias.

## Cuándo usarla

Cuando se solicite actualizar el progreso del proyecto o registrar cambios y verificaciones recientes.

## Inputs

| Input | Obligatorio | Descripción |
|---|---|---|
| Alcance solicitado | Sí | Área o periodo del proyecto que debe actualizarse. |
| Estado y evidencias | Sí | Archivos relevantes, cambios observables y, si corresponde, resultados reales de validación. |
| Próximos pasos | No | Pasos confirmados por el usuario o recomendaciones claramente identificadas como tales. |

## Procedimiento

1. Lee `memory-bank/progress.md` y revisa las evidencias disponibles para el alcance solicitado.
2. Conserva la información vigente y los cambios previos del desarrollador. Distingue lo implementado de lo propuesto.
3. Actualiza el estado, los cambios recientes y los próximos pasos pertinentes. Para las pruebas, registra el comando y el resultado real únicamente si están disponibles; indica cualquier fallo, advertencia o validación pendiente.
4. No inventes resultados ni expongas datos sensibles. Si falta información necesaria, solicita los datos o indica explícitamente que no se pudo verificar.

## Output esperado

`memory-bank/progress.md` actualizado y un resumen de lo documentado y de cualquier información pendiente de verificación.

## Criterios de aceptación

- El documento distingue estado actual, cambios recientes y próximos pasos.
- Cada afirmación nueva sobre implementación o validación está respaldada por evidencia disponible; no se atribuyen pruebas aprobadas sin un resultado real.
- Los pasos recomendados se identifican como propuestas y no como trabajo completado.
- La actualización conserva la información vigente y no incluye secretos ni datos sensibles.

## Ejemplo de entrada

Solicitud: actualizar el estado de selección. Evidencias: archivos modificados y salida de la suite ejecutada. Próximo paso propuesto: ampliar pruebas de integración.
