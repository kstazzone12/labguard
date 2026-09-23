# Delta checks

El módulo compara dos resultados del mismo paciente y analito sin inventar equivalencias. Calcula diferencia absoluta, diferencia porcentual e intervalo temporal.

## Validez

La comparación queda explícitamente no disponible cuando falta el resultado previo, el paciente o analito difieren, hay unidades o métodos diferentes, el intervalo temporal no es válido, el resultado previo es demasiado antiguo o cambia la referencia configurada. Los cambios de instrumento y referencia solo pueden permitirse mediante una política explícita; nunca se aplican conversiones implícitas.

## Reglas

`DeltaRuleConfig` permite reglas de porcentaje, diferencia absoluta y límites configurables, con alcance por analito y ventana temporal. También define severidad y recomendación de revisión. La política es configuración del laboratorio, no criterio clínico embebido.

Cada regla devuelve un `DELTA_EVENT`, activado o no. Los eventos no comparables conservan el motivo exacto, por ejemplo: `Delta check no disponible: método diferente.`
