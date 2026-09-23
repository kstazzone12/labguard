# Architecture

## Boundaries

- `backend/app/api`: HTTP boundary only.
- `backend/app/models`: transport and domain data structures.
- `backend/app/services`: application use cases.
- `backend/app/validation`: validation orchestration and rule execution boundary.
- `backend/app/qc`: internal quality control context.
- `backend/app/delta_checks`: historical comparisons.
- `backend/app/interferences`: possible interference signals.
- `backend/app/audit`: append-only traceability boundary.
- `backend/app/config`: environment configuration.
- `frontend/src`: human review interface, separated by workflow.
- `rules`: versioned declarative rules independent from Python code.
- `backend/app/engine`: rule loader, registry and evaluator independent from HTTP and persistence.
- `backend/app/analytical_consistency`: relaciones configurables y eventos de consistencia técnica.
- `backend/app/validation_engine`: orquestación, perfil de validación y cadena de auditoría.

## Controlled vocabulary

The implementation must keep these concepts distinct:

1. Data: observed or supplied values and context.
2. Rule: versioned configurable logic.
3. Alert: a signal emitted by an evaluated rule.
4. Recommendation: non-binding guidance for professional review.
5. Professional decision: an explicit human action recorded with audit data.

No module may transform an alert into an autonomous clinical decision or release a patient result.

## Rule Engine contract

Rules are loaded from YAML or JSON into a validated `RuleDefinition`. Conditions use generic field paths and operators; the engine does not contain clinical thresholds. `RuleEvaluator` emits one `RuleResult` per registered rule, with `executed`, `applicable`, `triggered`, `reason`, condition evidence, source, version and suggested action. Disabled or out-of-scope rules are returned as not executed with a reason, preserving audit visibility.

## Future adapters

LIS and instrument integrations belong behind adapters. They must preserve source identity, idempotency, timestamps and audit metadata. They are intentionally absent from this initial scaffold.
