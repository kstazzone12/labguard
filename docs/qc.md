# Control de calidad interno

## Capas

- `backend/app/qc/calculations.py`: matemática pura y determinista.
- `backend/app/qc/models.py`: material, lote, nivel, analito, método, instrumento, corrida, métricas, configuración y `QC_ALERT`.
- `backend/app/qc/rules.py`: funciones matemáticas para los códigos configurables `1_2s`, `1_3s`, `2_2s`, `R_4s`, `4_1s` y `10x`.
- `backend/app/qc/evaluator.py`: aplica configuración de laboratorio y crea decisiones/alertas.
- `backend/app/qc/synthetic.py`: observaciones sintéticas para Levey-Jennings.

## Métricas

- Diferencia: `resultado - media`.
- Z-score: `(resultado - media) / desviación_estándar`.
- SD index: distancia firmada en unidades de desviación estándar; en esta base es equivalente al z-score y se conserva como campo explícito para el contrato QC.
- CV: `desviación_estándar / |media| * 100`; es `null` cuando la media es cero.
- Posición: límites explícitos o límites derivados de `media +/- n * desviación_estándar`, solo cuando el laboratorio los configura.

## Configuración y decisión

Los códigos de regla no fijan severidad ni acción profesional. `QcRuleConfig` recibe esos valores junto con ventana, umbral y habilitación. `QcRuleEvaluator` devuelve decisiones aun cuando no se activa una regla; cuando se activa, crea un evento `QC_ALERT` con regla, control, resultado, evidencia, severidad y timestamp.

Esta fase no afirma criterios universales de aceptación. Las políticas concretas, límites y acciones pertenecen al laboratorio y deben configurarse explícitamente.
