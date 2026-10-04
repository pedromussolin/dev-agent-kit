/* Framework-independent presentation of the normalized logical pipeline model. */
const pipelineText = {
  pt: {
    pending: "Aguardando",
    running: "Em andamento",
    success: "Concluído",
    failed: "Falhou",
    skipped: "Ignorado",
    details: "Detalhes técnicos",
    operations: "operações",
    error: "Falha nesta etapa",
    duration: "Duração",
  },
  en: {
    pending: "Pending",
    running: "Running",
    success: "Succeeded",
    failed: "Failed",
    skipped: "Skipped",
    details: "Technical details",
    operations: "operations",
    error: "This phase failed",
    duration: "Duration",
  },
};
const pipelineIcons = {
  pending: "◌",
  running: "↻",
  success: "✓",
  failed: "!",
  skipped: "−",
};
function pipelineNode(tag, content, className) {
  const node = document.createElement(tag);
  node.textContent = content ?? "";
  if (className) node.className = className;
  return node;
}
function pipelineDuration(seconds) {
  if (seconds == null) return "—";
  const value = Math.round(seconds);
  return value < 60 ? `${value}s` : `${Math.floor(value / 60)}m ${value % 60}s`;
}
class PipelineView {
  constructor(container) {
    this.container = container;
  }
  render(phases, language = "pt") {
    const copy = pipelineText[language] || pipelineText.en;
    const open = new Set(
      Array.from(this.container.querySelectorAll("details[open]")).map(
        (node) => node.dataset.phaseId,
      ),
    );
    this.container.replaceChildren();
    for (const phase of phases) {
      const card = pipelineNode("section", null, `phase-card ${phase.status}`);
      const heading = pipelineNode("div", null, "phase-heading");
      heading.append(
        pipelineNode("span", pipelineIcons[phase.status] || "◌", "phase-icon"),
        pipelineNode("strong", phase.label[language] || phase.label.en),
        pipelineNode("span", copy[phase.status] || phase.status, "tag"),
        pipelineNode(
          "span",
          `${copy.duration}: ${pipelineDuration(phase.duration_seconds)}`,
          "small",
        ),
      );
      card.append(heading);
      if (phase.errors.length)
        card.append(
          pipelineNode(
            "p",
            `${copy.error}: ${phase.errors.join(" · ")}`,
            "phase-error",
          ),
        );
      const detail = pipelineNode("details");
      detail.dataset.phaseId = phase.id;
      detail.open = open.has(phase.id);
      detail.append(
        pipelineNode(
          "summary",
          `${copy.details} · ${phase.steps.length} ${copy.operations}`,
        ),
      );
      const operations = pipelineNode("ol");
      for (const step of phase.steps) {
        const row = pipelineNode("li");
        row.append(
          pipelineNode("strong", step.name),
          pipelineNode(
            "span",
            ` · ${copy[step.status]} · ${pipelineDuration(step.duration_seconds)}`,
            "small",
          ),
        );
        if (step.source_step)
          row.append(pipelineNode("p", step.source_step, "small"));
        if (step.summary) row.append(pipelineNode("p", step.summary));
        if (step.argv)
          row.append(
            pipelineNode("pre", JSON.stringify(step.argv), "technical-log"),
          );
        if (step.error)
          row.append(
            pipelineNode(
              "p",
              typeof step.error === "object"
                ? step.error.message || JSON.stringify(step.error)
                : step.error,
              "phase-error",
            ),
          );
        if (step.logs)
          row.append(pipelineNode("pre", step.logs, "technical-log"));
        operations.append(row);
      }
      detail.append(operations);
      card.append(detail);
      this.container.append(card);
    }
  }
}
window.PipelineView = PipelineView;
