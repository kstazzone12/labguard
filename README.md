# LABGUARD

Prototipo de investigación y desarrollo para apoyo a la validación de resultados de laboratorio bioquímico.

LABGUARD no es un sistema diagnóstico, no sustituye al profesional, no toma decisiones clínicas autónomas y no libera resultados automáticamente. Esta etapa usa exclusivamente datos ficticios o sintéticos.

## Arquitectura

El sistema se organiza en capas y contratos explícitos:

```text
React/TypeScript + Plotly (futuro)
							|
				FastAPI / Pydantic
							|
	Aplicación: casos, evaluación, revisión
							|
Dominio: datos -> reglas -> evidencia/alertas -> recomendación -> decisión profesional
							|
SQLAlchemy: SQLite (desarrollo) / PostgreSQL (futuro)
```

El motor de evaluación es independiente de FastAPI y de la base de datos. Carga reglas YAML/JSON versionadas, recibe un contexto normalizado y devuelve un evento por cada regla, incluso cuando no se activa. Una regla puede producir evidencia y una alerta; una recomendación es una orientación no vinculante; la decisión profesional es siempre una acción humana registrada posteriormente.

## Módulos previstos

- `domain`: entidades y contratos de resultados, muestras, QC, reglas, evidencia, alertas y revisiones.
- `engine`: evaluación determinista de reglas y composición de evidencias.
- `application`: casos de uso y orquestación.
- `adapters`: entradas sintéticas ahora; LIS, archivos y equipos en el futuro.
- `infrastructure`: persistencia, configuración y auditoría append-only.
- `frontend`: bandeja de revisión profesional, separando datos, señales y decisión.
- `rules`: YAML/JSON versionado, con parámetros dependientes de método, instrumento, fabricante o protocolo local.
- `engine`: loader, registry y evaluator declarativos, con evidencia por condición y resultado auditable.
- `qc`: cálculos internos, configuración de reglas QC y eventos `QC_ALERT`; preparado para políticas futuras.

El modelo incluye `discipline` para permitir química clínica, hematología, orina, coagulación, inmunología y endocrinología sin alterar el núcleo.

## Flujo de datos

1. Una fuente sintética entrega datos normalizados.
2. Se valida el esquema y se construye el contexto de muestra, resultados, QC e historial para delta checks.
3. El motor ejecuta las reglas aplicables y conserva la versión de cada regla.
4. Se generan evidencias explicables y, cuando corresponde, alertas y recomendaciones.
5. Un profesional revisa el caso y registra su decisión y comentario.
6. La auditoría registra actor, acción, fecha, caso, configuración y resultado resumido para reconstrucción posterior.

No se incorporan valores de referencia ni límites clínicos en el código. Los parámetros son configuración local y deben declararse junto con método, instrumento y versión del protocolo cuando aplique.

El módulo QC separa matemática, configuración y decisión del laboratorio. Calcula diferencia, z-score, SD index, CV y posición frente a límites configurados; no impone criterios universales.

El módulo Delta Check compara resultados del mismo paciente y analito con reglas configurables por porcentaje, diferencia absoluta, límites y ventana temporal. Si las unidades, métodos, instrumentos o intervalos de referencia no son comparables según la política, genera un `DELTA_EVENT` no disponible con el motivo explícito y no inventa equivalencias.

El `Analytical Consistency Engine` detecta inconsistencias matemáticas, analíticas o de calidad de datos mediante relaciones configurables entre analitos. Clasifica sus eventos como `DATA_ERROR`, `ANALYTICAL_REVIEW`, `SPECIMEN_REVIEW` o `CONFIGURATION_ERROR`, sin convertirlos en diagnósticos.

El `ValidationEngine` integra todas las etapas y genera un perfil con cadena de evidencia y auditoría. La recomendación del sistema permanece separada de `professional_decision`, que comienza sin registrar y solo puede completarse mediante revisión profesional.

## Estructura del repositorio

```text
backend/
	app/
		api/             # Rutas y contratos HTTP
		models/          # Modelos de dominio y transporte
		services/        # Casos de uso, sin lógica clínica aún
		validation/      # Orquestación futura de validación
		qc/              # Control de calidad interno
		delta_checks/    # Comparaciones históricas configurables
		interferences/   # Señales de posibles interferencias
		audit/           # Registro de trazabilidad
		config/          # Configuración del entorno
	tests/
frontend/
	src/
		dashboard/ samples/ results/ qc/ validation/ alerts/ configuration/
rules/
	chemistry/ hematology/ urinalysis/ general/
knowledge/
tests/
docs/
```

Las reglas viven fuera del código en `rules/`, están versionadas por Git y deben declarar sus parámetros locales. `knowledge/` queda reservado para documentación técnica controlada, no para valores clínicos implícitos. `tests/` contiene verificaciones transversales; los tests cercanos al backend pueden permanecer en `backend/tests/`.

SQLite se usa para desarrollo inicial y ya existe una migración Alembic base, manteniendo una interfaz compatible con PostgreSQL. La integración futura con LIS/equipamiento se hará mediante adaptadores idempotentes, con trazabilidad del origen y sin permitir que una fuente externa libere resultados.

## Ejecutar

```bash
python -m pip install -e '.[dev]'
uvicorn app.main:app --app-dir backend --reload
pytest

npm --prefix frontend install
npm --prefix frontend run dev
```

En terminales separadas, iniciar:

```bash
# Backend
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

# Frontend
npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173
```

El frontend queda en `http://localhost:5173/`, la salud de la API en `http://localhost:8000/health` y la evaluación integrada en `POST http://localhost:8000/validation/evaluate`. En un contenedor o Codespace debe utilizarse el reenvío de esos puertos.

## Uso del simulador

1. Abrir `http://localhost:5173/`.
2. En `SIMULATOR`, seleccionar `NORMAL SAMPLE`, `DELTA CHECK`, `QC FAILURE`, `HEMOLYZED SAMPLE` o `MULTIPLE FLAGS`.
3. Pulsar `Ejecutar escenario`.
4. Revisar `RESULT VALIDATION`, las alertas expandibles, la cadena de evidencia y `AUDIT TRAIL`.

Todos los escenarios son sintéticos. No hay conexión con instrumentos reales ni con LIS.