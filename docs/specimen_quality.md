# Specimen Quality

El módulo representa características preanalíticas de la muestra: hemólisis, lipemia, ictericia, volumen, tipo, tiempos, almacenamiento, observaciones y flags del instrumento.

Las interferencias son configuración, no afirmaciones universales. `InterferenceConfig` exige analito, alcance opcional por método/fabricante/instrumento, tipo, nivel, fuente, criterio, versión y fecha de vigencia.

La evaluación solo produce `REVIEW_REQUIRED` cuando un criterio configurado coincide. Una bandera de calidad sin criterio asociado produce `NO_CONFIGURED_INTERFERENCE`; no afirma que el resultado sea incorrecto.

Los ejemplos del repositorio están marcados como `DEMO` o `PLACEHOLDER` y no contienen niveles reales de interferencia.
