# Knowledge data

Este directorio contiene únicamente datos públicos o configuración versionada. Nunca contiene resultados profesionales ni identificadores de pacientes.

- `terminology/loinc.csv`: export oficial LOINC descargado por el mantenedor; no se generan códigos a mano.
- `sources/loinc.json`: versión, release, fuente, licencia, fecha de acceso y hash local.
- `units/ucum.json`: unidades y conversiones verificadas localmente. Si falta una entrada se devuelve `UNIT_CONVERSION_UNAVAILABLE`.
- `reference_intervals/`, `qc/`, `interferences/` y `rules/`: configuración versionada, separada del dato profesional.

La aplicación no necesita una API externa para ejecutar validaciones ni solicita credenciales al usuario final. La actualización de datasets es una operación de mantenimiento explícita.
