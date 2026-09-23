import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { useState } from "react";

import "./styles.css";

const backendModules = [
  ["API", "Contratos HTTP y punto de entrada", "Preparado"],
  ["Modelos", "Entidades y esquemas de datos", "Implementado"],
  ["Servicios", "Casos de uso y orquestación", "Base creada"],
  ["Validación", "Contexto para revisión profesional", "Base creada"],
  ["QC", "Control de calidad interno", "Modelo creado"],
  ["Controles delta", "Historial de resultados", "Modelo creado"],
  ["Calidad de muestra", "Calidad preanalítica e interferencias", "Implementado"],
  ["Consistencia analítica", "Relaciones configurables entre analitos", "Implementado"],
  ["Validación", "Perfil y cadena de evidencia", "Implementado"],
  ["Interferencias", "Parámetros por método y protocolo", "Configurable"],
  ["Auditoría", "Eventos trazables y solo de adición", "Modelo creado"],
  ["Motor de reglas", "Cargador, registro y evaluador", "Implementado"],
  ["Configuración", "Entorno y base de datos", "Implementado"],
];

const frontendAreas = [
  "Panel",
  "Muestras",
  "Resultados",
  "QC",
  "Validación",
  "Alertas",
  "Configuración",
];

const entities = [
  "PATIENT",
  "SAMPLE",
  "ANALYTE",
  "RESULT",
  "INSTRUMENT",
  "METHOD",
  "QC_RUN",
  "QC_RESULT",
  "REFERENCE_INTERVAL",
  "INTERFERENCE",
  "RULE",
  "ALERT",
  "VALIDATION_EVENT",
  "AUDIT_EVENT",
];

const projectFacts = [
  ["Fuente de datos", "Sintética exclusivamente"],
  ["Persistencia", "SQLite + migración Alembic"],
  ["Servidor", "Python + FastAPI"],
  ["Interfaz", "React + TypeScript + Vite"],
  ["QC", "Métricas + 6 reglas configurables"],
  ["Control delta", "Comparaciones configurables"],
  ["Calidad de muestra", "Preanalítica + interferencias configuradas"],
  ["Consistencia", "Relaciones matemáticas configurables"],
  ["Validación", "Perfil con auditoría por etapa"],
  ["Reglas", "YAML/JSON versionado"],
  ["Motor de reglas", "YAML + registro + evaluador"],
  ["Pruebas", "pytest: 45 pruebas aprobadas"],
];

const qcRuns = [99.8, 100.4, 101.0, 98.8, 100.2, 99.4, 100.8, 101.2, 99.6, 100.0];
const qcChartX = (index: number) => 48 + index * 46;
const qcChartY = (value: number) => 202 - ((value - 94) / 12) * 160;

type ScenarioKey = "normal" | "delta" | "qc" | "hemolyzed" | "multiple";

const scenarioLabels: Record<ScenarioKey, string> = {
  normal: "NORMAL SAMPLE",
  delta: "DELTA CHECK",
  qc: "QC FAILURE",
  hemolyzed: "HEMOLYZED SAMPLE",
  multiple: "MULTIPLE FLAGS",
};

const demoTimestamps = {
  current: "2026-01-15T08:00:00Z",
  previous: "2026-01-14T08:00:00Z",
};

function createScenarioPayload(scenario: ScenarioKey) {
  const isDelta = scenario === "delta" || scenario === "multiple";
  const isQcFailure = scenario === "qc" || scenario === "multiple";
  const isHemolyzed = scenario === "hemolyzed" || scenario === "multiple";
  const isMultiple = scenario === "multiple";
  const currentValue = isDelta ? 120 : 100;
  const previousValue = 100;

  return {
    result: {
      id: "result-current-001",
      patient_id: "SYNTH-001",
      analyte_code: "SYN-A",
      numeric_value: currentValue,
      value: String(currentValue),
      unit: "synthetic-unit",
      method_code: "METHOD-1",
      instrument_code: "INSTRUMENT-1",
      sample_id: "sample-current-001",
      timestamp: demoTimestamps.current,
    },
    sample: {
      sample_id: "sample-current-001",
      analyte: "SYN-A",
      method: "METHOD-1",
      instrument: "INSTRUMENT-1",
      manufacturer: "SYNTHETIC-MANUFACTURER",
      sample_type: "synthetic-serum",
      hemolysis: isHemolyzed ? "HIGH" : null,
      lipemia: null,
      icteria: null,
      volume: 1,
      volume_unit: "synthetic-unit",
      processing_time: demoTimestamps.current,
      storage_condition: "DEMO_REFRIGERATED",
      instrument_flags: isHemolyzed ? { sample_quality: "DEMO_FLAG" } : {},
    },
    qc_observations: isQcFailure ? [{
      control: { material: "DEMO", lot: "DEMO-LOT", level: "1", analyte: "SYN-A", method: "METHOD-1", instrument: "INSTRUMENT-1" },
      run_number: 1,
      timestamp: demoTimestamps.current,
      result: 106.4,
      mean: 100,
      standard_deviation: 2,
    }] : [],
    qc_rules: isQcFailure ? [{ rule_id: "qc-demo-1_3s", code: "1_3s", name: "DEMO QC 1_3s", severity: "review", suggested_action: "Solicitar revisión profesional del QC.", window_size: 1, threshold_sd: 3 }] : [],
    previous_results: {
      current: { patient_id: "SYNTH-001", sample_id: "sample-current-001", result_id: "result-current-001", analyte: "SYN-A", value: currentValue, unit: "synthetic-unit", timestamp: demoTimestamps.current, method: "METHOD-1", instrument: "INSTRUMENT-1" },
      previous: isDelta ? { patient_id: "SYNTH-001", sample_id: "sample-previous-001", result_id: "result-previous-001", analyte: "SYN-A", value: previousValue, unit: "synthetic-unit", timestamp: demoTimestamps.previous, method: "METHOD-1", instrument: "INSTRUMENT-1" } : null,
    },
    delta_rules: isDelta ? [{ rule_id: "delta-demo-20", name: "DEMO delta", rule_type: "percentage", percentage_limit: 10, severity: "review", recommendation: "Solicitar revisión profesional del delta.", source: "DEMO_PLACEHOLDER" }] : [],
    interferences: isHemolyzed ? [{ interference_id: "interference-demo", analyte: "SYN-A", method: "METHOD-1", manufacturer: "SYNTHETIC-MANUFACTURER", instrument: "INSTRUMENT-1", interference_type: "DEMO_HEMOLYSIS", level: "HIGH", source_type: "laboratory_SOP", source_reference: "DEMO_PLACEHOLDER", criterion: { field: "hemolysis", operator: "equals", value: "HIGH" }, version: "DEMO-1.0", effective_date: "2026-01-01", suggested_action: "Solicitar revisión de la muestra." }] : [],
    consistency: { sample_id: "sample-current-001", measurements: [{ analyte: "SYN-A", value: currentValue }, { analyte: "SYN-B", value: isMultiple ? 90 : 100, source: "calculated" }] },
    consistency_rules: isMultiple ? [{ rule_id: "consistency-demo", name: "DEMO consistency", relation: "difference", involved_analytes: ["SYN-A", "SYN-B"], category: "ANALYTICAL_REVIEW", severity: "review", explanation: "La diferencia supera la tolerancia configurada.", recommendation: "Solicitar revisión de consistencia.", parameters: { tolerance: 5 }, version: "DEMO-1.0", source: "DEMO_PLACEHOLDER" }] : [],
    rule_context: { result: { numeric_value: currentValue }, sample: {}, qc: {}, previous: {}, evaluated_at: demoTimestamps.current },
    rules: [],
    laboratory_configuration: { configuration_version: "DEMO-1.0", laboratory_identifier: "SYNTHETIC-ENV", settings: { scenario } },
  };
}

function App() {
  const [selectedScenario, setSelectedScenario] = useState<ScenarioKey>("normal");
  const [validationProfile, setValidationProfile] = useState<any | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [expandedEvidence, setExpandedEvidence] = useState<Record<number, boolean>>({});

  const runScenario = async () => {
    setIsRunning(true);
    setApiError(null);
    try {
      const response = await fetch("http://localhost:8000/validation/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(createScenarioPayload(selectedScenario)),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setValidationProfile(await response.json());
      setExpandedEvidence({});
    } catch (error) {
      setApiError(`No se pudo ejecutar el escenario: ${String(error)}`);
    } finally {
      setIsRunning(false);
    }
  };

  const reviewItems = validationProfile?.review_items ?? [];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">
          <span className="brand-dot" />
          <span>LABGUARD</span>
        </div>
        <p className="sidebar-caption">Prototipo de apoyo a la validación</p>
        <nav aria-label="Navegación del proyecto">
          <a className="active" href="#validacion">VALIDACIÓN</a>
          <a href="#muestras">MUESTRAS</a>
          <a href="#resultados">RESULTADOS</a>
          <a href="#qc">QC</a>
          <a href="#alertas">ALERTAS</a>
          <a href="#reglas">REGLAS</a>
          <a href="#auditoria">AUDITORÍA</a>
          <a href="#simulador">SIMULADOR</a>
          <a href="#configuracion">CONFIGURACIÓN</a>
        </nav>
        <div className="sidebar-footer">
          <span className="status-led" />
          <span>Entorno de desarrollo</span>
        </div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Centro de proyecto · versión 0.1.0</p>
            <h1>Resumen de LABGUARD</h1>
          </div>
          <div className="mode-pill">Datos sintéticos únicamente</div>
        </header>

        <section className="hero-panel" id="resumen">
          <div>
            <p className="section-kicker">Motor de apoyo a la validación bioquímica</p>
            <h2>Una vista común para datos, evidencia y revisión profesional.</h2>
            <p className="hero-copy">
              LABGUARD organiza resultados, muestras, control de calidad y señales
              configurables. No diagnostica, no libera resultados y no reemplaza
              la decisión del profesional.
            </p>
          </div>
          <div className="hero-status">
            <span className="status-ring">✓</span>
            <strong>Base del proyecto lista</strong>
            <span>Servidor, interfaz, persistencia y pruebas iniciales</span>
          </div>
        </section>

        <section className="validation-workbench" id="validacion">
          <div className="workbench-heading">
            <div>
              <p className="section-kicker">Revisión profesional asistida · datos sintéticos</p>
              <h2>RESULT VALIDATION</h2>
            </div>
            <span className={`system-status ${reviewItems.length ? "needs-review" : "clear"}`}>
              <i /> {reviewItems.length ? "Professional review required" : "No additional review flags"}
            </span>
          </div>

          <div className="validation-columns">
            <div className="validation-main-column">
              <section className="workbench-card" id="resultados">
                <div className="card-heading"><span className="card-index">01</span><h3>RESULTADO</h3></div>
                <div className="result-grid">
                  <div><span>Analito</span><strong>{validationProfile?.result?.analyte_code ?? "SYN-A"}</strong></div>
                  <div><span>Valor</span><strong>{validationProfile?.result?.value ?? "100"}</strong></div>
                  <div><span>Unidad</span><strong>{validationProfile?.result?.unit ?? "synthetic-unit"}</strong></div>
                  <div><span>Método</span><strong>{validationProfile?.result?.method_code ?? "METHOD-1"}</strong></div>
                  <div><span>Instrumento</span><strong>{validationProfile?.result?.instrument_code ?? "INSTRUMENT-1"}</strong></div>
                  <div><span>Fecha</span><strong>15 ene 2026 · 08:00</strong></div>
                </div>
              </section>

              <section className="workbench-card" id="muestras">
                <div className="card-heading"><span className="card-index">02</span><h3>SAMPLE QUALITY</h3></div>
                <div className="result-grid quality-grid">
                  <div><span>Hemólisis</span><strong>{validationProfile?.specimen_events?.some((event: any) => event.status === "REVIEW_REQUIRED") ? "HIGH" : "No señal"}</strong></div>
                  <div><span>Lipemia</span><strong>Sin señal</strong></div>
                  <div><span>Ictericia</span><strong>Sin señal</strong></div>
                  <div><span>Volumen</span><strong>1.0 synthetic-unit</strong></div>
                  <div><span>Flags</span><strong>{validationProfile?.specimen_events?.length ? "Configurables" : "Ninguno"}</strong></div>
                  <div><span>Estado</span><strong>{validationProfile?.has_preanalytical_problem ? "Revisión" : "Disponible"}</strong></div>
                </div>
              </section>

              <section className="workbench-card" id="qc">
                <div className="card-heading"><span className="card-index">03</span><h3>QUALITY CONTROL</h3></div>
                <div className="status-row"><strong>{validationProfile?.qc_decisions?.some((decision: any) => decision.triggered) ? "QC rule triggered" : "QC sin señales activas"}</strong><span>{validationProfile?.qc_decisions?.length ? `${validationProfile.qc_decisions.length} regla(s) ejecutada(s)` : "Sin corrida cargada"}</span></div>
              </section>

              <section className="workbench-card" id="delta">
                <div className="card-heading"><span className="card-index">04</span><h3>DELTA CHECK</h3></div>
                <div className="delta-validation-grid"><div><span>Resultado previo</span><strong>{validationProfile?.delta_events?.[0]?.previous_result_id ? "100" : "No disponible"}</strong></div><div><span>Resultado actual</span><strong>{validationProfile?.result?.value ?? "100"}</strong></div><div><span>Cambio absoluto</span><strong>{validationProfile?.delta_events?.[0]?.absolute_delta ?? "—"}</strong></div><div><span>Cambio porcentual</span><strong>{validationProfile?.delta_events?.[0]?.percentage_delta ? `${validationProfile.delta_events[0].percentage_delta}%` : "—"}</strong></div></div>
                <div className="inline-state">{validationProfile?.has_delta_check ? "Delta check triggered" : "Sin delta check activado"}</div>
              </section>

              <section className="workbench-card">
                <div className="card-heading"><span className="card-index">05</span><h3>ANALYTICAL CONSISTENCY</h3></div>
                <div className="status-row"><strong>{validationProfile?.has_consistency_problem ? "Analytical consistency review" : "Sin inconsistencias activas"}</strong><span>{validationProfile?.consistency_events?.length ?? 0} relación(es) evaluada(s)</span></div>
              </section>

              <section className="workbench-card evidence-card" id="alertas">
                <div className="card-heading"><span className="card-index">06</span><h3>EVIDENCE CHAIN</h3></div>
                <div className="evidence-chain"><span>Resultado</span><b>↓</b><span>QC</span><b>↓</b><span>Muestra</span><b>↓</b><span>Delta</span><b>↓</b><span>Interferencia</span><b>↓</b><span>Consistencia</span><b>↓</b><span>Reglas</span><b>↓</b><strong>Revisión profesional</strong></div>
                <div className="alert-list">
                  {reviewItems.length === 0 && <p className="empty-state">No hay alertas activas en este perfil.</p>}
                  {reviewItems.map((item: any, index: number) => (
                    <article className="alert-row" key={`${item.source}-${index}`}>
                      <div className="alert-row-summary"><span className="alert-marker" /><div><strong>{item.source}</strong><p>{item.reason}</p></div><button type="button" onClick={() => setExpandedEvidence((current) => ({ ...current, [index]: !current[index] }))}>{expandedEvidence[index] ? "Ocultar evidencia" : "Ver evidencia"}</button></div>
                      {expandedEvidence[index] && <pre className="evidence-detail">{JSON.stringify(item.evidence, null, 2)}</pre>}
                    </article>
                  ))}
                </div>
              </section>
            </div>

            <aside className="validation-side-column">
              <section className="simulator-card" id="simulador">
                <p className="section-kicker">Datos ficticios · ejecución local</p>
                <h3>SIMULATOR</h3>
                <p>Generá un perfil sintético y observá cómo cada módulo aporta evidencia.</p>
                <div className="scenario-list">
                  {(Object.keys(scenarioLabels) as ScenarioKey[]).map((scenario) => <button type="button" className={selectedScenario === scenario ? "scenario-button selected" : "scenario-button"} key={scenario} onClick={() => setSelectedScenario(scenario)}><span>{String(Object.keys(scenarioLabels).indexOf(scenario) + 1).padStart(2, "0")}</span>{scenarioLabels[scenario]}</button>)}
                </div>
                <button className="run-button" type="button" disabled={isRunning} onClick={runScenario}>{isRunning ? "Procesando…" : "Ejecutar escenario"}</button>
                {apiError && <p className="api-error">{apiError}</p>}
              </section>
              <section className="audit-card" id="auditoria">
                <div className="card-heading"><span className="card-index">AUDIT</span><h3>AUDIT TRAIL</h3></div>
                <p>{validationProfile ? `${validationProfile.audit_trail.length} etapas registradas` : "Ejecutá un escenario para registrar la cadena."}</p>
                <div className="audit-list">{(validationProfile?.audit_trail ?? []).map((entry: any) => <div key={entry.audit_id}><span className="audit-dot" /><strong>{entry.stage}</strong><small>{new Date(entry.timestamp).toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" })}</small></div>)}</div>
              </section>
              <section className="professional-card" id="configuracion"><span className="note-label">DECISIÓN PROFESIONAL</span><strong>{validationProfile?.professional_decision?.status === "recorded" ? "Registrada" : "No registrada"}</strong><p>El software recomienda. La decisión pertenece al profesional.</p></section>
            </aside>
          </div>
        </section>

        <section className="facts-grid" aria-label="Datos del proyecto">
          {projectFacts.map(([label, value]) => (
            <article className="fact-card" key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </article>
          ))}
        </section>

        <section className="section-block" id="arquitectura">
          <div className="section-heading">
            <div>
              <p className="section-kicker">01 · Capas del sistema</p>
              <h2>Arquitectura modular</h2>
            </div>
            <p>Las señales se conservan separadas de la decisión profesional.</p>
          </div>
          <div className="architecture-flow">
            <div><span>01</span><strong>Datos</strong><small>Paciente, muestra, resultados y QC</small></div>
            <div><span>02</span><strong>Configuración</strong><small>Método, instrumento, protocolo y reglas</small></div>
            <div><span>03</span><strong>Evidencia</strong><small>Alertas y recomendaciones explicables</small></div>
            <div><span>04</span><strong>Revisión</strong><small>Acción profesional auditada</small></div>
          </div>
          <div className="module-grid">
            {backendModules.map(([name, description, status]) => (
              <article className="module-card" key={name}>
                <div className="module-card-top"><strong>{name}</strong><span>{status}</span></div>
                <p>{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section-block split-section" id="modelo">
          <div>
            <div className="section-heading compact">
              <div>
                <p className="section-kicker">02 · Persistencia</p>
                <h2>Modelo de datos</h2>
              </div>
            </div>
            <p className="body-copy">
              El paciente sintético está separado del contexto analítico. Cada
              resultado conserva muestra, analito, unidad, tiempo, método,
              instrumento, estado, flags, calidad y referencia utilizada.
            </p>
            <div className="entity-list">
              {entities.map((entity) => <span key={entity}>{entity}</span>)}
            </div>
          </div>
          <div className="sample-card">
            <div className="sample-card-header"><span>DATOS DEMO</span><strong>minimal_case.json</strong></div>
            <div className="sample-row"><span>Identificador</span><strong>SYNTH-001</strong></div>
            <div className="sample-row"><span>Muestra</span><strong>Suero sintético · procesada</strong></div>
            <div className="sample-row"><span>Resultado</span><strong>SYN-ANALYTE-01 · 42.0</strong></div>
            <div className="sample-row"><span>Referencia</span><strong className="muted-value">No suministrada</strong></div>
            <div className="sample-row"><span>Interferencias</span><strong className="muted-value">No configuradas</strong></div>
          </div>
        </section>

        <section className="section-block qc-visual-section" id="qc">
          <div className="section-heading">
            <div>
              <p className="section-kicker">03 · Control de calidad interno</p>
              <h2>Levey-Jennings sintético</h2>
            </div>
            <p>Media 100 · SD 2 · 10 corridas ficticias</p>
          </div>
          <div className="qc-layout">
            <div className="chart-card">
              <div className="chart-header"><strong>SYN-ANALYTE-01</strong><span>SYNTH-LOT-001 · level-1</span></div>
              <svg className="qc-chart" viewBox="0 0 520 240" role="img" aria-label="Gráfica de Levey-Jennings con datos sintéticos">
                {[94, 96, 98, 100, 102, 104, 106].map((value) => (
                  <g key={value}>
                    <line className="chart-grid-line" x1="40" x2="500" y1={qcChartY(value)} y2={qcChartY(value)} />
                    <text className="chart-axis-label" x="4" y={qcChartY(value) + 4}>{value}</text>
                  </g>
                ))}
                <line className="chart-limit-line three-sd" x1="40" x2="500" y1={qcChartY(106)} y2={qcChartY(106)} />
                <line className="chart-limit-line two-sd" x1="40" x2="500" y1={qcChartY(104)} y2={qcChartY(104)} />
                <line className="chart-mean-line" x1="40" x2="500" y1={qcChartY(100)} y2={qcChartY(100)} />
                <line className="chart-limit-line two-sd" x1="40" x2="500" y1={qcChartY(96)} y2={qcChartY(96)} />
                <line className="chart-limit-line three-sd" x1="40" x2="500" y1={qcChartY(94)} y2={qcChartY(94)} />
                <polyline className="qc-line" points={qcRuns.map((value, index) => `${qcChartX(index)},${qcChartY(value)}`).join(" ")} />
                {qcRuns.map((value, index) => (
                  <circle className="qc-point" cx={qcChartX(index)} cy={qcChartY(value)} key={index} r="4" />
                ))}
                {qcRuns.map((_, index) => <text className="chart-run-label" key={`run-${index}`} x={qcChartX(index) - 3} y="226">{index + 1}</text>)}
              </svg>
              <div className="chart-legend"><span><i className="legend-dot" />Resultado</span><span><i className="legend-line mean" />Media</span><span><i className="legend-line limits" />Límites configurados</span></div>
            </div>
            <div className="qc-summary">
              <span className="note-label">MÉTRICAS DEL MÓDULO</span>
              <div><strong>Diferencia</strong><span>resultado − media</span></div>
              <div><strong>Z-score</strong><span>distancia en unidades SD</span></div>
              <div><strong>SD index</strong><span>distancia firmada</span></div>
              <div><strong>CV</strong><span>SD / |media| × 100</span></div>
              <div><strong>QC_ALERT</strong><span>evento estructurado con evidencia</span></div>
            </div>
          </div>
        </section>

        <section className="section-block delta-section" id="delta">
          <div className="section-heading">
            <div>
              <p className="section-kicker">04 · Comparación histórica</p>
              <h2>Control delta</h2>
            </div>
            <p>Resultado actual vs. resultado previo del mismo analito</p>
          </div>
          <div className="delta-layout">
            <div className="delta-comparison">
              <div className="delta-measurement previous-measurement">
                <span>PREVIO · 14 ENE 2026</span>
                <strong>100</strong>
                <small>SYN-ANALYTE-01 · synthetic-unit</small>
              </div>
              <div className="delta-arrow">→</div>
              <div className="delta-measurement current-measurement">
                <span>ACTUAL · 15 ENE 2026</span>
                <strong>120</strong>
                <small>SYN-ANALYTE-01 · synthetic-unit</small>
              </div>
            </div>
            <div className="delta-metrics">
              <div><span>Diferencia absoluta</span><strong>+20</strong></div>
              <div><span>Diferencia porcentual</span><strong>+20%</strong></div>
              <div><span>Intervalo temporal</span><strong>24 h</strong></div>
            </div>
          </div>
          <div className="delta-footer">
            <div className="delta-validity"><span className="validity-dot" />Comparación disponible</div>
            <p>La política puede bloquear la comparación cuando cambian unidad, método, instrumento, referencia o antigüedad. No se inventan equivalencias.</p>
          </div>
        </section>

        <section className="section-block specimen-section" id="specimen">
          <div className="section-heading">
            <div>
              <p className="section-kicker">05 · Calidad preanalítica</p>
              <h2>Calidad de muestra</h2>
            </div>
            <p>DEMO/PLACEHOLDER · criterio configurable</p>
          </div>
          <div className="specimen-layout">
            <div className="specimen-facts">
              <div><span>ANALYTE</span><strong>SYN-ANALYTE-01</strong></div>
              <div><span>SPECIMEN</span><strong>synthetic-serum</strong></div>
              <div><span>HEMÓLISIS</span><strong className="quality-high">ALTA</strong></div>
              <div><span>VOLUMEN</span><strong>1.0 synthetic-unit</strong></div>
              <div><span>ALMACENAMIENTO</span><strong>DEMO_REFRIGERATED</strong></div>
              <div><span>INDICADOR DEL INSTRUMENTO</span><strong>DEMO_FLAG</strong></div>
            </div>
            <div className="specimen-evidence">
              <span className="note-label">EVIDENCIA</span>
              <strong>Indicador de calidad de muestra</strong>
              <p>Posible impacto: <b>Interferencia configurada</b></p>
              <div className="review-status"><span className="review-dot" />REVISIÓN REQUERIDA</div>
              <small>Solo se muestra porque existe un criterio DEMO configurado con fuente y versión.</small>
            </div>
          </div>
        </section>

        <section className="section-block consistency-section" id="consistencia">
          <div className="section-heading">
            <div>
              <p className="section-kicker">06 · Relaciones entre analitos</p>
              <h2>Consistencia analítica</h2>
            </div>
            <p>CONSISTENCY_EVENT · caso DEMO/PLACEHOLDER</p>
          </div>
          <div className="consistency-layout">
            <div className="consistency-values">
              <div><span>ANALITO A · MEDIDO</span><strong>120</strong><small>SYN-A · synthetic-unit</small></div>
              <div className="relation-mark">−</div>
              <div><span>ANALITO B · CALCULADO</span><strong>100</strong><small>SYN-B · synthetic-unit</small></div>
              <div className="relation-result"><span>DIFERENCIA</span><strong>20</strong><small>Tolerancia configurada: 10</small></div>
            </div>
            <div className="consistency-event">
              <span className="note-label">CONSISTENCY_EVENT</span>
              <strong>Revisión de consistencia activada</strong>
              <p>La relación calculada difiere del valor observado más allá de la tolerancia configurada.</p>
              <div className="event-category"><span className="category-dot" />ANALYTICAL_REVIEW</div>
              <small>No es un diagnóstico. La regla, la tolerancia y la recomendación son configurables.</small>
            </div>
          </div>
          <div className="category-list">
            <span><b>DATA_ERROR</b> Datos o unidades incompatibles</span>
            <span><b>ANALYTICAL_REVIEW</b> Relación requiere revisión</span>
            <span><b>SPECIMEN_REVIEW</b> Índice de muestra inconsistente</span>
            <span><b>CONFIGURATION_ERROR</b> Regla incompleta o inválida</span>
          </div>
        </section>

        <section className="section-block validation-section" id="validacion">
          <div className="section-heading">
            <div>
              <p className="section-kicker">07 · Cadena de evidencia</p>
              <h2>Perfil de validación</h2>
            </div>
            <p>VALIDATION_PROFILE · auditoría por etapa</p>
          </div>
          <div className="validation-chain">
            <span>RESULTADO</span><i>↓</i><span>QC</span><i>↓</i><span>MUESTRA</span><i>↓</i><span>DELTA</span><i>↓</i><span>CONSISTENCIA</span><i>↓</i><span>REGLAS</span><i>↓</i><strong>PERFIL</strong>
          </div>
          <div className="validation-summary">
            <div><span>QUÉ SE EVALUÓ</span><strong>Resultado, muestra, QC, historial y reglas configuradas</strong></div>
            <div><span>RECOMENDACIÓN DEL SISTEMA</span><strong>Se recomienda revisión profesional.</strong></div>
            <div><span>DECISIÓN PROFESIONAL</span><strong className="not-recorded">No registrada</strong></div>
          </div>
          <div className="validation-note"><span className="status-led" /> Cada etapa conserva datos utilizados, configuración, evidencia, versión y timestamp en el AUDIT TRAIL.</div>
        </section>

        <section className="section-block" id="reglas">
          <div className="section-heading">
            <div>
              <p className="section-kicker">08 · Configuración y trazabilidad</p>
              <h2>Reglas fuera del código</h2>
            </div>
            <p>Versionadas en Git · parámetros locales explícitos</p>
          </div>
          <div className="rules-layout">
            <div className="rule-tree">
              <div><span className="tree-mark">/</span><strong>rules</strong></div>
              <div className="tree-child">chemistry</div>
              <div className="tree-child">hematology</div>
              <div className="tree-child">urinalysis</div>
              <div className="tree-child">general</div>
            </div>
            <div className="audit-note">
              <span className="note-label">SEPARACIÓN DE CONCEPTOS</span>
              <div className="concept-row"><strong>Dato</strong><span>Valor y contexto suministrado</span></div>
              <div className="concept-row"><strong>Regla</strong><span>Configuración versionada</span></div>
              <div className="concept-row"><strong>Alerta</strong><span>Señal para revisar</span></div>
              <div className="concept-row"><strong>Recomendación</strong><span>Orientación no vinculante</span></div>
              <div className="concept-row"><strong>Decisión</strong><span>Acción humana auditada</span></div>
            </div>
          </div>
          <div className="engine-strip">
            <span className="note-label">MOTOR DE REGLAS · ACTIVO EN EL PROTOTIPO</span>
            <span>Una evaluación devuelve un evento por regla, activada o no, con versión, evidencia, aplicabilidad y motivo.</span>
          </div>
        </section>

        <section className="section-block boundary-section" id="alcance">
          <div className="boundary-copy">
            <p className="section-kicker">09 · Límites del prototipo</p>
            <h2>Apoyo, nunca autonomía clínica.</h2>
            <p>Esta versión no implementa criterios Westgard, controles delta, diagnóstico, liberación automática ni conexiones con LIS o equipamiento real. El motor disponible solo ejecuta reglas sintéticas configurables.</p>
          </div>
          <div className="future-list">
            <span>Próximo: integrar evaluación en el flujo API</span>
            <span>Próximo: revisión de alertas</span>
            <span>Futuro: adaptadores LIS</span>
          </div>
        </section>

        <footer>LABGUARD · Investigación y desarrollo · Sin datos reales de pacientes</footer>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
