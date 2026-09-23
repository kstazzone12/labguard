# Validation Engine

`ValidationEngine` integra resultado, muestra, QC, resultados previos, reglas, interferencias, consistencia analítica y configuración del entorno.

El resultado es un `ValidationProfile` con una cadena de evidencia por etapas:

`RESULT -> QC -> SPECIMEN_QUALITY -> DELTA_CHECK -> INTERFERENCE -> CONSISTENCY -> RULE_ENGINE -> VALIDATION_PROFILE -> PROFESSIONAL_REVIEW`

Cada etapa registra entrada resumida, configuración, versión disponible, salida, evidencia y timestamp en `audit_trail`.

El perfil responde mediante sus colecciones y propiedades si existe problema de QC, problema preanalítico, delta activado o inconsistencia. `system_recommendation` solo expresa una recomendación del software. `professional_decision` comienza como `not_recorded` y no es completada por el motor.

La fase incluye cinco escenarios sintéticos de integración en `backend/tests/test_validation_engine.py`.
