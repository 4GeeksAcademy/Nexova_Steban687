# Instrucciones para agentes

Estas reglas se aplican a todo el monorepo. Síguelas antes de explorar o modificar código.

## Lectura obligatoria al inicio de cada sesión

Antes de planificar cambios o editar archivos, lee estos documentos del banco de memoria en este orden:

1. `memory-bank/proyectbrief.md` — contexto y dominio del proyecto.
2. `memory-bank/techContext.md` — arquitectura, stack y decisiones técnicas.
3. `memory-bank/progress.md` — estado actual, cambios recientes y próximos pasos.

Si alguno falta o no se puede leer, indícalo y no inventes su contenido.

## Ubicación del código de producto

Usa las carpetas existentes de la plantilla y sigue los README de cada ruta antes de trabajar en ella. No crees un segundo árbol de frontend o API en otra ubicación.

| Ruta desde la raíz | Uso cuando se cree o amplíe |
|---|---|
| `uis/` | Proyectos frontend de la empresa; sigue [uis/README.es.md](uis/README.es.md). |
| `uis/website/` | Web corporativa pública, con página de entrada en la ruta `/`. Alinea la marca y el contenido con [BREAFING.md](BREAFING.md), el briefing existente del proyecto. |
| `uis/backoffice/` | Aplicación interna, separada del sitio público, con layout propio y vista de entrada en la ruta `/`. |
| `services/` | APIs y servicios backend; sigue [services/README.es.md](services/README.es.md). |

`uis/website/` y `uis/backoffice/` son ubicaciones previstas, no aplicaciones que deban crearse hasta que una tarea lo requiera.

## Flujo obligatorio antes de cada commit

Completa los siguientes pasos en orden antes de ejecutar un commit:

1. **Comprobar el estado del repositorio:** revisa la rama y `git status`; identifica los cambios previos del desarrollador y no los descartes ni los incluyas por accidente.
2. **Revisar el alcance:** inspecciona el diff completo y confirma que cada cambio corresponde a la tarea solicitada.
3. **Validar los cambios:** ejecuta las pruebas, el lint y las comprobaciones de tipos pertinentes. Si alguna validación falla o no puede ejecutarse, resuélvelo o informa el bloqueo; no presentes el cambio como verificado.
4. **Revisar documentación y artefactos:** actualiza la documentación directamente relacionada y comprueba que no se hayan añadido secretos, credenciales, archivos generados, cachés ni resultados temporales.
5. **Preparar el staging:** añade solo los archivos previstos, ejecuta `git diff --cached --check` e inspecciona el diff staged completo.
6. **Autorizar y crear el commit:** crea el commit solo después de completar satisfactoriamente los pasos anteriores y confirmar que no requiere modificar rutas protegidas. Usa un mensaje claro y descriptivo.

Si un paso no se cumple, detén el proceso antes del commit e informa qué falta.

## Rutas protegidas

No modifiques estas rutas sin confirmación explícita del desarrollador para la tarea actual:

- **Briefing y contexto del proyecto:** `BREAFING.md`, `CONTEXT.md`, `CONTEXT.es.md`, `memory-bank/proyectbrief.md` y `memory-bank/techContext.md`.
- **Datos fuente y de evaluación:** `data/raw/` y `data/eval/`.
- **Infraestructura y workflows:** `infra/` y `workflows/`.
- **Secretos y credenciales:** archivos `.env*`, `*.pem`, `*.key` y archivos cuyo nombre indique que contienen secretos o credenciales.

Si una tarea parece requerir cambios en una ruta protegida, detente y solicita confirmación explícita antes de editarla. La autorización para modificar un archivo no autoriza a mostrar, copiar ni incluir secretos o credenciales en un commit.
