# Declarative rules

Rules are loaded from YAML or JSON and versioned independently from Python code. Each rule declares scope, conditions, severity, suggested action, source, protocol, effective date and enabled state.

The files in this repository are deliberately synthetic demonstrations. They do not contain clinical thresholds. Local laboratory configuration must supply any method-, instrument-, manufacturer- or protocol-dependent parameters.

A rule emits an auditable event. It never makes a diagnosis, releases a patient result or replaces professional review.
