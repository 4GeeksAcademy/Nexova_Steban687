# Progreso del proyecto

## Estado actual

El proyecto Nexova cuenta con una primera implementación del flujo de selección de candidatos. Incluye un servicio de negocio, un agente para comunicaciones, tipos compartidos y una demo que recorre el pipeline de reclutamiento.

El agente dispone de plantillas de comunicación en español e inglés para los estados de candidatura, confirmaciones de entrevista y seguimientos.

La ubicación prevista del código de producto está documentada en [AGENTS.md](../AGENTS.md#ubicación-del-código-de-producto). La plantilla ya incluye `uis/` y `services/`; las aplicaciones `uis/website/` y `uis/backoffice/` se crearán allí cuando se necesiten.

## Últimos cambios

- Se alinearon las claves de las plantillas de estado con los estados de candidatura `new`, `shortlisted` y `rejected`. Esto corrige la prueba que detectaba la diferencia entre los nombres esperados y los disponibles.
- Se ejecutó la suite del servicio y del agente de selección: **41 pruebas aprobadas**.

Comando ejecutado:

```bash
pytest services/selection/test_service.py agents/selection/test_agent.py -v
```

La ejecución también reportó 74 advertencias de obsolescencia por el uso de `datetime.utcnow()` en el servicio compartido. No impidieron que las pruebas pasaran.

## Próximos pasos previstos

Estos pasos son recomendaciones para continuar el desarrollo:

1. Sustituir `datetime.utcnow()` por una fecha y hora UTC con zona horaria y volver a ejecutar las pruebas.
2. Ampliar las pruebas de integración para cubrir el flujo completo de reclutamiento y sus casos límite.
3. Automatizar la ejecución de pruebas en CI para detectar regresiones en futuros cambios.