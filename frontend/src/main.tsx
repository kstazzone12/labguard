import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { ImportWorkbench } from "./ImportWorkbench";
import { KnowledgeBasePanel } from "./KnowledgeBasePanel";
import "./styles.css";

function App() {
  return (
    <div className="app-shell professional-shell">
      <aside className="sidebar">
        <div className="brand-mark"><span className="brand-dot" /><span>LABGUARD</span></div>
        <p className="sidebar-caption">Validación profesional de resultados de laboratorio</p>
        <nav aria-label="Navegación principal">
          <a className="active" href="#datos-locales">DATOS LOCALES</a>
          <a href="#importacion">IMPORTACIÓN</a>
          <a href="#registros">REGISTROS</a>
          <a href="#privacidad">PRIVACIDAD</a>
          <a href="#knowledge-base">KNOWLEDGE BASE</a>
        </nav>
        <div className="sidebar-footer"><span className="status-led" /><span>Almacenamiento local activo</span></div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div><p className="eyebrow">Entorno profesional · datos locales</p><h1>Centro de trabajo</h1></div>
          <div className="mode-pill">Sin API key · sin cuenta externa</div>
        </header>

        <section className="professional-intro" id="datos-locales">
          <div>
            <p className="section-kicker">Flujo de trabajo protegido</p>
            <h2>Cargá resultados reales y revisalos en este navegador.</h2>
            <p>Importá archivos CSV o JSON, comprobá su estructura antes de guardarlos y mantené los datos profesionales bajo tu control. LABGUARD no envía resultados a servicios externos.</p>
          </div>
          <div className="privacy-panel" id="privacidad"><span className="status-ring">✓</span><strong>Privacidad local</strong><span>Almacenamiento local · eliminación bajo demanda</span></div>
        </section>

        <div id="importacion"><ImportWorkbench /></div>
        <KnowledgeBasePanel />

        <section className="professional-guidance" id="registros">
          <div><span className="note-label">FLUJO DE REVISIÓN</span><strong>Importar</strong><p>Seleccioná un archivo y verificá la vista previa.</p></div>
          <div><span className="note-label">ESTADO DEL DATO</span><strong>Validar</strong><p>Los errores críticos bloquean la importación.</p></div>
          <div><span className="note-label">DECISIÓN</span><strong>Revisar</strong><p>El software apoya la revisión profesional y no libera resultados.</p></div>
        </section>

        <footer>LABGUARD · Los datos permanecen localmente en este navegador.</footer>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
