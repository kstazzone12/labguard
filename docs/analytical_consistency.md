# Analytical Consistency Engine

Este módulo detecta inconsistencias matemáticas, analíticas o de calidad de datos. No diagnostica enfermedades ni utiliza rangos clínicos implícitos.

Cada `ConsistencyRuleConfig` declara la relación, analitos, parámetros, categoría, severidad, explicación, recomendación, versión y fuente. El evaluador produce un `CONSISTENCY_EVENT` por regla.

Las categorías distinguen:

- `DATA_ERROR`: valores, unidades o límites configurados incompatibles.
- `ANALYTICAL_REVIEW`: discrepancia entre relaciones o resultados calculados/medidos.
- `SPECIMEN_REVIEW`: inconsistencia relacionada con índices de muestra.
- `CONFIGURATION_ERROR`: falta un parámetro o dato necesario para evaluar la regla.

Los límites de demostración del dataset están marcados como `DEMO_PLACEHOLDER` y no representan criterios clínicos.
