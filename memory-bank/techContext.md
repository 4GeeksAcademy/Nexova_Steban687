# Tech Context — Nexova Solutions

> Basado en el briefing corporativo de Nexova Solutions (consultora de RRHH y selección de talento, Valencia + Miami).
> Documento generado a partir del análisis de necesidades tecnológicas y de infraestructura detectadas en los 8 departamentos.

---

## 1. Stack Tecnológico

### 1.1 Estado Actual (Legado)

| Sistema | Propósito | Estado |
|---------|-----------|--------|
| **HubSpot** | CRM de ventas | Subutilizado (~40% de adopción), datos inconsistentes |
| **Zendesk Legacy** | Helpdesk / soporte al cliente | Obsoleto, sin integraciones, sin base de conocimiento |
| **Google Workspace** | Tejido conectivo (email, Drive, Forms, Sheets) | Uso intensivo pero desestructurado; hojas de cálculo como sistemas |
| **ATS Interno (2010)** | Seguimiento de candidatos | Construido a medida, no escalable, sin API moderna |
| **Google Forms + Sheets** | Inscripciones formación, evaluaciones desempeño | Manual, sin trazabilidad |
| **PDF + Word en Drive** | Catálogo de formación, base de conocimiento soporte | Estático, sin búsqueda, sin versionado |
| **Informe semanal PDF manual** | Reporting ejecutivo | 4–8 h/gerente/semana, datos con >=7 días de retraso |
| **Sin telemetría ni logging centralizado** | — | El equipo de tecnología se entera de los fallos por los usuarios |
| **Despliegues manuales** | — | Sin CI/CD, sin automatización |

### 1.2 Stack Propuesto (Target)

#### Backend / APIs

| Capa | Tecnologías sugeridas |
|------|----------------------|
| Lenguaje principal | **Python 3.11+** (servicios de IA/ML, pipelines de datos, agentes) y **TypeScript (Node.js)** (APIs transaccionales, BFFs, webhooks) |
| Framework API | **FastAPI** (Python) o **Express/NestJS** (TypeScript) según contexto |
| Base de datos relacional | **PostgreSQL 15+** con extensiones (pgvector para embeddings, pg_stat_statements para monitorización) |
| Base de datos vectorial | **pgvector** (sobre PostgreSQL) o **Qdrant** / **Chroma** para RAG |
| Cache / Colas | **Redis** (caché, rate-limiting, colas Celery / BullMQ) |
| ORM / Query Builder | **SQLAlchemy** / **Prisma** / **Drizzle** |
| Documentación API | **OpenAPI 3.x** (generado automáticamente desde FastAPI o NestJS) |

#### Frontend / UI

| Capa | Tecnologías sugeridas |
|------|----------------------|
| Framework web | **Next.js 14+** (React + SSR) para dashboards, portales y paneles |
| UI Components | **Tailwind CSS** + **Shadcn/ui** o **Radix UI** |
| Charting / Dashboards | **Recharts**, **Apache ECharts**, o **Streamlit** para prototipos analíticos |
| Web corporativa | **Next.js** con SSR/SSG, marcado **schema.org**, optimización SEO/GEO |

#### IA / Machine Learning

| Capa | Tecnologías sugeridas |
|------|----------------------|
| LLMs | **OpenAI GPT-4 / GPT-4o**, **Claude 3.5**, o **Llama 3 70B** (vía API o self-hosted) |
| Embeddings | **text-embedding-3-large** (OpenAI), **multilingual-e5-large** (Hugging Face) |
| RAG Framework | **LangChain** / **LlamaIndex** — para búsqueda semántica sobre candidatos, base de conocimiento y políticas RRHH |
| Orquestación de agentes | **LangGraph**, **CrewAI** o **AutoGen** para agentes multi-departamento |
| NLP / Clasificación | **Hugging Face Transformers**, **spaCy**, **scikit-learn** |
| CV Scoring | Pipeline custom con extracción por LLM + embeddings + ranking explicable (SHAP/LIME) |
| Recomendación formativa | Filtrado colaborativo + contenido (modelos híbridos: surprise, lightFM, o LLM-based) |
| Sentiment Analysis | Fine-tuning BERT multilingüe o API de clasificación de OpenAI |

#### Data / Infraestructura

| Capa | Tecnologías sugeridas |
|------|----------------------|
| Data Pipeline | **Prefect** / **Apache Airflow** — orquestación de pipelines ETL |
| Transformaciones | **dbt** (data build tool) sobre PostgreSQL |
| Data Warehouse | **PostgreSQL** (modelo dimensional) o **BigQuery** si escala |
| Monitorización | **Grafana** + **Prometheus** + **OpenTelemetry** (logs, métricas, trazas) |
| Logging centralizado | **Loki** (Grafana) / **ELK Stack** (Elasticsearch, Logstash, Kibana) |
| Alertas | **Grafana Alerting** + webhooks a Slack/Teams |
| Contenedores | **Docker** + **docker-compose** (dev) + **Kubernetes** / **AWS ECS** / **Google Cloud Run** (prod) |
| CI/CD | **GitHub Actions** / **GitLab CI** |
| Cloud | **AWS** (preferente por ecosistema) o **Google Cloud Platform** |

---

## 2. Decisiones de Arquitectura

### 2.1 Principios Generales

1. **Arquitectura basada en dominios (Domain-Driven)** — cada departamento es un dominio acotado con su propio modelo de datos, lógica y UI. Se comunican vía eventos y APIs síncronas solo cuando es estrictamente necesario.

2. **Data Mesh / Data Product** — cada dominio es propietario de sus datos y los expone como un producto consumible por otros dominios (especialmente el tablero ejecutivo unificado y el informe semanal).

3. **AI-First, no AI-Addon** — la IA no es una característica opcional sino el núcleo de la ventaja competitiva. Cada pipeline debe estar diseñado para incorporar modelos desde el día 1 (scoring de CVs, matching, RAG, agentes).

4. **API-as-a-Product** — toda funcionalidad se expone mediante API (REST o GraphQL) para que cualquier equipo o agente pueda consumirla.

5. **Observabilidad desde el inicio** — telemetría, logging y trazabilidad no son post-hoc; cada servicio publica métricas y logs estructurados desde el primer commit.

### 2.2 Decisiones Clave por Departamento / Sistema

#### Operaciones de Selección (Core Business)

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Scoring de CVs | Pipeline LLM + embeddings + regresión explicable | Necesita ranking + explicabilidad (SHAP) |
| Matching candidato-vacante | RAG sobre embeddings de CVs y descripciones de puesto | Búsqueda semántica > búsqueda por palabras clave |
| Portal de candidatos | Frontend Next.js + API REST (FastAPI) sobre PostgreSQL | Estado en tiempo real, auto-gestionado por el candidato |
| Agente de comunicación | Agente LLM + cola de tareas (Redis + Celery/BullMQ) | Envíos automáticos con seguimiento por template |

#### Formación Corporativa

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Catálogo online | Base de datos relacional + Next.js frontend + búsqueda full-text + vectorial | Búsqueda híbrida (texto + semántica) |
| Sistema de recomendación | Modelo híbrido (contenido + filtrado colaborativo) o LLM-based | Perfiles de cliente muy variados; necesidad de personalización |
| Chatbot asesor | RAG sobre catálogo + agente conversacional con contexto de perfil | Guía al usuario hacia programas relevantes |
| Progreso alumno | Modelo relacional + webhooks de plataformas externas (LMS) | Seguimiento independiente del proveedor de formación |

#### Atención al Cliente (Outsourcing)

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Chatbot primera línea | RAG sobre base de conocimiento (embeddings + LLM) | Objetivo: resolver 40% sin intervención humana |
| Base de conocimiento | Documentos indexados en vector DB + búsqueda semántica | Centralizada, versionada, auto-actualizable |
| Dashboard soporte | Tiempo real vía WebSockets + métricas desde eventos | Visibilidad inmediata de carga de trabajo y SLA |
| Sentiment Analysis | Clasificador multilingüe sobre tickets de texto | Detectar clientes insatisfechos antes de escalada |

#### Ventas y Desarrollo de Negocio

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Pipeline de ventas | Integración con HubSpot API + datos en PostgreSQL local | No depender exclusivamente de HubSpot; tener copia analítica |
| Automatización prospección | Secuencias basadas en eventos + agente LLM para personalización | Primer contacto -> seguimiento -> cierre o descarte |
| Agente de propuestas | RAG sobre base de casos de éxito + datos del prospecto | Sugerir el ángulo de propuesta más adecuado |

#### Recursos Humanos (Interno)

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Portal RRHH | Frontend Next.js + API sobre PostgreSQL | Autogestión de vacaciones, ausencias, consultas |
| Onboarding automatizado | Máquina de estados + checklists progresivos | Consistencia y trazabilidad |
| Agente interno RRHH | RAG sobre policies and benefits + LLM | Respuestas inmediatas sin intervención de Patricia |

#### Marketing y Comunicación

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Rediseño web | Next.js SSR + schema.org + Core Web Vitals | SEO/GEO, accesibilidad, velocidad |
| Pipeline contenidos | Editor asistido por IA + flujo de revisión humano | Acelerar producción sin perder calidad |
| Panel métricas | Eventos -> Data Warehouse -> Grafana / Metabase | Saber qué convierte, no solo cuántas visitas |

#### Tecnología e Infraestructura (Propio equipo)

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Logging centralizado | OpenTelemetry + Grafana Loki o ELK | Trazabilidad extremo a extremo |
| Pipeline de datos único | Prefect/Airflow + dbt -> alimenta todos los tableros | Una fuente de verdad; los KPIs se calculan una vez |
| Monitorización | Prometheus + Grafana + alertas | Detección proactiva de fallos |
| Agente de ingeniería | RAG sobre documentación técnica + diagramas C4 | Responde preguntas de arquitectura al equipo |

#### Dirección Ejecutiva

| Decisión | Opción elegida | Motivo |
|----------|---------------|--------|
| Tablero unificado | Data Warehouse agregado + dashboard en Grafana/Metabase | KPIs en tiempo real de todas las áreas |
| Informe semanal | Generado por agente LLM + pipeline de datos | Automatizado, siempre actualizado, sin esfuerzo manual |
| Asistente ejecutivo | Chatbot RAG + query sobre Data Warehouse | Consultas en lenguaje natural sobre el negocio |

### 2.3 Diagrama de Arquitectura Conceptual

`
[Usuarios / Clientes / Candidatos / Agentes]
         |
         v
+------------------- GATEWAY / API Layer -------------------+
|  FastAPI / Next.js API Routes / WebSockets                |
+--------+----------+----------+----------+-----------------+
         |          |          |          |
+--------v----------v----------v----------v-----------------+
|                     Domain Services                        |
|  +----------+ +----------+ +----------+ +--------------+  |
|  |Selection | | Training | | Support  | | Sales / Mkt  |  |
|  |  Service | | Service  | | Service  | |    Service   |  |
|  +----------+ +----------+ +----------+ +--------------+  |
|  +----------+ +----------+ +----------+                  |
|  |   HR     | |  Infra   | |  Exec    |                  |
|  | Service  | | Service  | | Service  |                  |
|  +----------+ +----------+ +----------+                  |
+------------------------------------------------------------+
         |
+--------v---------------------------------------------------+
|                   AI / ML Layer                             |
|  +-------------+ +--------------+ +--------------------+  |
|  | RAG Engine  | | CV Scoring   | | Recommendation     |  |
|  | (LlamaIndex)| | Pipeline     | | Engine             |  |
|  +-------------+ +--------------+ +--------------------+  |
|  +-------------+ +--------------+ +--------------------+  |
|  | Sentiment   | | Agent        | | Embeddings / NLP   |  |
|  | Analyzer    | | Orchestrator | | (HF / OpenAI)      |  |
|  +-------------+ +--------------+ +--------------------+  |
+------------------------------------------------------------+
         |
+--------v---------------------------------------------------+
|                   Data Layer                                |
|  +------------+ +----------+ +----------+ +------------+  |
|  | PostgreSQL | | Vector DB| |  Redis   | | Object     |  |
|  | (relational)| |(pgvector)| | (cache)  | | Storage (S3)| |
|  +------------+ +----------+ +----------+ +------------+  |
+------------------------------------------------------------+
         |
+--------v---------------------------------------------------+
|              Observability & Data Pipeline                  |
|  +-------------+ +--------------+ +--------------------+  |
|  | OpenTelemetry| |  Prefect /   | |  Grafana +        |  |
|  | + Prometheus | |  Airflow     | |  Prometheus + Loki | |
|  +-------------+ +--------------+ +--------------------+  |
|  +------------------------------------------------------+  |
|  |  Data Warehouse (PostgreSQL analítico) + dbt          |  |
|  +------------------------------------------------------+  |
+------------------------------------------------------------+
`

---

## 3. Restricciones Técnicas

### 3.1 Restricciones de Negocio

| # | Restricción | Implicación técnica |
|---|-------------|-------------------|
| R01 | **SLA de soporte: 24h** - el chatbot de primera línea debe resolver >=40% sin escalar a humano | El sistema RAG debe tener alta precisión (>=90% en consultas frecuentes); los fallos deben escalar con contexto completo |
| R02 | **Datos sensibles de candidatos y clientes** - cumplimiento RGPD (UE) + CCPA (EE.UU.) | Los embeddings y logs no deben contener PII; cifrado en reposo y en tránsito; política de retención de datos |
| R03 | **Equipo de tecnología pequeño (6 personas)** - mantenibilidad y simplicidad crítica | Preferir soluciones managed (SaaS) sobre self-hosted cuando sea posible; minimizar herramientas distintas; documentación obligatoria |
| R04 | **Adopción de usuario inconsistente** (ej. HubSpot usado al 40%) | Las UIs deben ser intuitivas y requerir cero configuración; las integraciones con herramientas existentes deben ser transparentes |
| R05 | **La IA debe ser explicable** - el scoring de CVs y las recomendaciones deben poder justificarse | Incluir SHAP/LIME o técnicas similares en pipelines de scoring; el ranking debe ir acompañado de razones legibles |
| R06 | **Multilingüismo** - la empresa opera en España y EE.UU. (español e inglés) | Todos los sistemas de NLP deben ser multilingües (embeddings, clasificadores, LLMs); las UIs deben soportar i18n |
| R07 | **La información ejecutiva no puede tener más de 24h de retraso** | Los pipelines de datos deben ejecutarse al menos cada hora; el dashboard ejecutivo debe refrescar en tiempo real (o casi) |
| R08 | **Presupuesto acotado** - startup de 120 empleados,  facturación | Optimizar costes de API (caching, batching, modelos más pequeños para tareas simples); priorizar MVP por departamento |

### 3.2 Restricciones Técnicas / de Infraestructura

| # | Restricción | Implicación |
|---|-------------|-------------|
| T01 | **No existe logging ni telemetría actualmente** | Implementar observabilidad desde el día 1; sin ella no se puede medir SLA, rendimiento ni impacto |
| T02 | **Despliegues manuales sin CI/CD** | Automatizar builds, tests y despliegues con GitHub Actions; contenedores Docker para entornos reproducibles |
| T03 | **Integraciones con sistemas legados** (HubSpot, Zendesk Legacy, ATS 2010) | Desarrollar adaptadores / wrappers; exponer APIs uniformes; planificar migración progresiva |
| T04 | **Google Workspace como base de datos** | Migrar datos de Sheets y Forms a bases de datos reales; mantener sincronización bidireccional durante transición |
| T05 | **Sin estándar de datos entre departamentos** | Definir un modelo de datos común (ver packages/shared/types/) y contratos de API; cada dominio expone datos estandarizados |
| T06 | **Los agentes de IA deben poder interoperar** | Los agentes (selección, RRHH, soporte, ingeniería, ejecutivo) deben compartir infraestructura RAG y de orquestación pero tener contextos aislados |
| T07 | **La web corporativa actual (2019) es lenta, no accesible, sin SEO** | El rediseño debe cumplir Core Web Vitals, WCAG 2.1 AA, y schema.org |

### 3.3 Restricciones de Desarrollo y Entrega

| # | Restricción | Implicación |
|---|-------------|-------------|
| D01 | **Proyecto de AI Engineering - 4Geeks Academy** | Debe entregarse como proyecto formativo con código limpio, tests, documentación y despliegue demostrable |
| D02 | **Múltiples departamentos con distintas velocidades de entrega** | Priorizar por impacto: Operaciones de Selección (core business) -> Soporte (SLA urgente) -> Ventas (oportunidad) -> RRHH/Formación -> Marketing -> Ejecutivo |
| D03 | **Código compartido** - existe packages/shared/types/ para tipos comunes | Extender el paquete compartido con tipos de dominio (Entrevista, Candidato, Curso, Ticket, Prospecto) según evolucione el proyecto |
| D04 | **Agentes como entregables centrales** | Cada agente debe tener: definición de rol (system prompt), herramientas (tools), memoria (contexto), y tests de evaluacion |

### 3.4 Restricciones de Datos

| # | Restricción | Implicación |
|---|-------------|-------------|
| DA01 | **Base de datos de candidatos (ATS legacy) sin API moderna** | Necesario ETL inicial + adaptador en tiempo real; considerar migración completa a PostgreSQL |
| DA02 | **Catálogo de formación en PDF desactualizado** | Digitalizar y estructurar en base de datos; el PDF pasa a ser una vista exportable, no la fuente de verdad |
| DA03 | **Base de conocimiento de soporte en un Word en Drive** | Indexar documentos existentes en vector DB; establecer proceso de actualización continua |
| DA04 | **No hay métricas históricas de RRHH** | Iniciar recolección desde el día 1; los paneles mostrarán en construcción para datos pasados |
| DA05 | **El CRM (HubSpot) tiene datos inconsistentes** | Implementar validación en la capa de integración; no asumir limpieza de datos origen |

---

## 4. Resumen de Tecnologías Clave

| Propósito | Tecnología | Justificación |
|-----------|-----------|---------------|
| RAG / Búsqueda semántica | LlamaIndex + pgvector | Stack unificado (PostgreSQL); evita vectores externos |
| Scoring de CVs | LLM + Embeddings + SHAP | Explicabilidad + precisión |
| Agentes conversacionales | LangGraph / CrewAI | Orquestación multi-agente con estado |
| Dashboards | Grafana + Metabase | Open source; conecta directo a PostgreSQL |
| Pipeline de datos | Prefect + dbt | Orquestación Python-native + transformaciones SQL |
| Logging | OpenTelemetry + Grafana Loki | Estándar abierto; integración nativa con Grafana |
| Frontend | Next.js 14+ + Tailwind | SSR, SEO, tipado fuerte con TypeScript |
| API Backend | FastAPI (Python) / Next.js API (TypeScript) | Según complejidad: ML->Python, CRUD->TypeScript |
| Contenedores | Docker + docker-compose | Portabilidad; mismo stack en local, CI y producción |
| CI/CD | GitHub Actions | Integración nativa con el repositorio; matrices de test |
| Vector DB | pgvector (PostgreSQL extension) | Evita base de datos separada; embeddings + datos relacionales juntos |

---

> **Nota:** Este documento es vivo. Debe actualizarse cuando se tomen decisiones concretas de tecnologia (POC completados, cambios de proveedor, restricciones descubiertas). Cada decision debe registrarse con fecha, responsable y motivacion en la seccion de Decisiones de Arquitectura.

## Arqurtectura final del monorepo.

Nexova_Steban687/
├── demo/
│   ├── __init__.py
│   ├── recruitment_pipeline.py   ← Demo completa (ejecutable)
│   └── run_all.py                ← Lanzador de todas las demos
├── services/
│   ├── shared/base_service.py    ← Clase base con logging + eventos
│   └── selection/
│       ├── service.py            ← Servicio core con scoring IA
│       └── test_service.py       ← 11+ tests
├── agents/
│   ├── orchestrator.py           ← Router de eventos multi-agente
│   └── selection/
│       ├── agent.py              ← Agente comunicaciones bilingüe
│       └── test_agent.py         ← 16+ tests
├── packages/shared/types/index.ts ← Tipos TypeScript (8 departamentos)
├── memory-bank/
│   ├── context.md                ← Contexto del proyecto
│   └── techContext.md            ← Stack, decisiones, restricciones
└── pyproject.toml                ← Configuración del proyecto


# Capas implementadas

📊 Capas implementadas:

|Capa|Archivo|Función|
|---|---|---|
|Tipos compartidos|index.ts|Interfaces TypeScript para 8 departamentos|
|Servicio Core|service.py|Lógica de negocio: scoring IA, matching, scheduling|
|Tests Servicio|test_service.py|Cobertura: CRUD, scoring, edge cases|
|Agente|agent.py|Tool-based: 5 herramientas, plantillas ES/EN, auditoría|
|Tests Agente|test_agent.py|Cobertura: 8 clases de test, 16+ tests|
|Orquestador|orchestrator.py|Router de eventos, extensible a 6+ agentes|
|Demo|recruitment_pipeline.py|Pipeline completo: servicio → agente → orquestador|


# Demo del pipeline completo (reclutamiento con datos falsos)
python -m demo.recruitment_pipeline

# O lanzador general
python -m demo.run_all

# Tests
pytest services/selection/test_service.py agents/selection/test_agent.py -v

