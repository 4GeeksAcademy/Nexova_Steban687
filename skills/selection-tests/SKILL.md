---
name: selection-tests
description: Ejecuta las pruebas del servicio y del agente de selección y comunica su resultado.
---

# Pruebas de selección

## Objetivo

Ejecutar la suite de selección y entregar un informe fiel de su resultado.

## Cuándo usarla

Cuando se solicite comprobar o informar el estado de las pruebas del servicio y del agente de selección.

## Inputs

| Input | Obligatorio | Descripción |
|---|---|---|
| Raíz del monorepo | Sí | Directorio desde el que se ejecuta la suite. |
| Entorno Python | Sí | Python compatible con `pyproject.toml` y `pytest` disponible. |

## Procedimiento

1. Desde la raíz del monorepo, ejecuta:

   ```bash
   pytest services/selection/test_service.py agents/selection/test_agent.py -v
   ```

2. Usa la salida y el código de salida del comando para identificar pruebas aprobadas, fallidas u omitidas y advertencias.
3. Comunica el resultado con el comando ejecutado, los recuentos que aparezcan en la salida y las causas de los fallos o bloqueos. No incluyas datos sensibles de la salida.
4. Si el comando no se puede ejecutar o no termina, informa el bloqueo; no presentes las pruebas como aprobadas.

## Output esperado

Un informe con el comando, resultado general, recuentos disponibles, advertencias y detalles relevantes de fallos o bloqueos.

## Criterios de aceptación

- Se ejecuta el comando indicado desde la raíz y se registra su código de salida, o se informa por qué no pudo ejecutarse.
- El informe incluye los recuentos y advertencias presentes en la salida, sin inventar resultados.
- Solo se informa que la suite pasó si el comando terminó correctamente, con al menos una prueba aprobada y sin pruebas fallidas ni errores; se mencionan las pruebas omitidas.
- Ante fallos o un bloqueo, se identifican las pruebas afectadas o la causa disponible; no se declara éxito.

## Ejemplo de informe

Para una ejecución hipotética con pruebas aprobadas y sin advertencias: `Comando: pytest ... -v; resultado: aprobado; recuentos: 2 aprobadas, 0 fallidas; advertencias: ninguna.`
