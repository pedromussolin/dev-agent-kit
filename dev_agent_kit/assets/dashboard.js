const $ = (id) => document.getElementById(id);
let selected = null,
  stream = null,
  lastEvent = 0,
  events = [],
  runs = [],
  lang = "pt",
  selectedWorkflow = null;
const pipelineView = new PipelineView($("stages"));
const strings = {
  pt: {
    subtitle: "Acompanhe decisões, trabalho e entrega.",
    filter: "Projetos e tarefas",
    empty: "Selecione uma execução para acompanhar os agentes.",
    calls: "Atribuições",
    tokens: "Tokens observados",
    delivery: "Entrega",
    cost: "Custo financeiro desconhecido",
    timeline: "O que está acontecendo",
    cancel: "Parar execução",
    unknown: "Uso indisponível em",
    attempt: "Tentativa",
    idle: "Nenhuma execução registrada. Inicie uma tarefa pela CLI.",
    failed: "Falha ao consultar o executor.",
    stop: "Parada solicitada. O executor encerrará o trabalho e preservará as evidências.",
    footer:
      "Mensagens públicas e atividade dos agentes. Raciocínio privado, prompts e saídas brutas de ferramentas não são exibidos. O uso é interrompido quando observado; uma requisição em andamento pode ultrapassar o limite.",
    states: {
      pending: "Aguardando",
      running: "Em execução",
      succeeded: "Concluído",
      failed: "Falhou",
      blocked: "Precisa de atenção",
      cancelled: "Interrompido",
      invalidated: "Precisa ser revalidado",
    },
    roles: {
      developer: "Desenvolvedor",
      "qa-engineer": "QA",
      "technical-reviewer": "Revisor técnico",
      "product-manager": "PM",
      "product-owner": "PO",
      "software-architect": "Arquiteto",
      "security-engineer": "Segurança",
    },
    activities: {
      running_command: "Executando ferramenta",
      editing_files: "Alterando arquivos",
      using_tool: "Consultando ferramenta",
    },
  },
  en: {
    subtitle: "Follow decisions, work and delivery.",
    filter: "Projects and tasks",
    empty: "Select a run to follow its agents.",
    calls: "Assignments",
    tokens: "Observed tokens",
    delivery: "Delivery",
    cost: "Monetary cost unknown",
    timeline: "What is happening",
    cancel: "Stop execution",
    unknown: "Usage unavailable for",
    attempt: "Attempt",
    idle: "No runs yet. Start a task from the CLI.",
    failed: "Could not inspect executor state.",
    stop: "Stop requested. The executor will terminate work and preserve evidence.",
    footer:
      "Public agent updates and activity only. Private reasoning, prompts and raw tool output are not displayed. Usage is interrupted when observed; an in-flight request may exceed a threshold.",
    states: {
      pending: "Waiting",
      running: "Running",
      succeeded: "Completed",
      failed: "Failed",
      blocked: "Needs attention",
      cancelled: "Cancelled",
      invalidated: "Needs revalidation",
    },
    roles: {
      developer: "Developer",
      "qa-engineer": "QA",
      "technical-reviewer": "Technical reviewer",
    },
    activities: {
      running_command: "Running a tool",
      editing_files: "Editing files",
      using_tool: "Consulting a tool",
    },
  },
};
function text(node, value) {
  node.textContent = value ?? "";
}
function el(tag, content, cls) {
  let n = document.createElement(tag);
  text(n, content);
  if (cls) n.className = cls;
  return n;
}
function s() {
  return strings[lang];
}
function role(value) {
  return s().roles[value] || value || "Executor";
}
async function api(path, options) {
  let r = await fetch(path, options);
  if (!r.ok) throw Error(s().failed + " (" + r.status + ")");
  return r.json();
}
function renderRuns() {
  let filter = $("filter").value.toLowerCase();
  $("runs").replaceChildren();
  for (let r of runs.filter((r) =>
    (r.task_id + " " + r.project_id).toLowerCase().includes(filter),
  )) {
    let b = el("button", null, "run");
    b.setAttribute("aria-current", r.id === selected);
    b.append(
      el("strong", r.task_id),
      el("div", r.project_id, "small"),
      el("span", s().states[r.status] || r.status, "tag " + r.status),
    );
    b.onclick = () => choose(r.id);
    $("runs").append(b);
  }
  if (!runs.length) $("runs").append(el("p", s().idle));
}
function renderEvents() {
  $("timeline").replaceChildren();
  for (let e of events.slice(-150)) {
    let p = e.payload,
      description = p.message || s().activities[p.activity] || e.type;
    if (e.type === "agent.usage")
      description =
        "Tokens: " +
        (
          p.usage.total_tokens ??
          (p.usage.input_tokens || 0) + (p.usage.output_tokens || 0)
        ).toLocaleString();
    let n = el("div", null, "event");
    n.append(
      el(
        "span",
        new Date(e.timestamp).toLocaleTimeString() + " · " + role(p.role_id),
        "small",
      ),
      el("span", description),
    );
    $("timeline").append(n);
  }
}
async function refresh() {
  try {
    runs = await api("/api/runs");
    renderRuns();
    await renderWorkflows();
    if (selected) await detail();
    if (selectedWorkflow) await workflowDetail();
    $("connection").textContent = "Local · online";
  } catch (e) {
    text($("connection"), s().failed);
  }
}
async function detail() {
  const identity = selected;
  let r = await api("/api/runs/" + encodeURIComponent(identity));
  if (identity !== selected) return;
  $("detail").hidden = false;
  $("empty").hidden = true;
  text($("task"), r.task_id);
  text($("goal"), r.goal);
  text(
    $("evidence"),
    lang === "pt"
      ? r.evidence_current === true
        ? "Evidência atual"
        : r.evidence_current === false
          ? "Código alterado: evidência precisa de revalidação"
          : "Evidência indisponível neste ambiente"
      : r.evidence_current === true
        ? "Current evidence"
        : r.evidence_current === false
          ? "Source changed: evidence needs revalidation"
          : "Evidence unavailable in this environment",
  );
  text($("status"), s().states[r.status] || r.status);
  $("status").className = "tag " + r.status;
  text($("calls"), r.agent_calls + " / " + r.limits.max_agent_calls);
  text(
    $("attempts"),
    s().attempt + " " + r.attempts + " / " + r.limits.max_attempts,
  );
  text(
    $("tokens"),
    r.invocations.reduce((sum, i) => sum + i.total_tokens, 0).toLocaleString() +
      " / " +
      (r.limits.max_total_tokens || 0).toLocaleString(),
  );
  let unknown = r.invocations.filter((i) => !i.usage).length;
  text($("usage-note"), unknown ? s().unknown + " " + unknown : "");
  text($("delivery"), r.delivery_mode);
  text($("error"), r.error ? r.error.category + ": " + r.error.message : "");
  $("cancel").disabled = r.status !== "running";
  pipelineView.render(r.phases || [], lang);
}
function choose(id) {
  selectedWorkflow = null;
  $("workflow-detail").hidden = true;
  if (stream) stream.close();
  selected = id;
  lastEvent = 0;
  events = [];
  renderRuns();
  detail().catch((e) => text($("error"), e.message));
  stream = new EventSource("/api/runs/" + encodeURIComponent(id) + "/events");
  stream.onmessage = (e) => {
    let value = JSON.parse(e.data);
    if (value.id <= lastEvent) return;
    lastEvent = value.id;
    events.push(value);
    renderEvents();
  };
  stream.onerror = () => {
    if (runs.find((r) => r.id === selected)?.status !== "running")
      stream.close();
  };
}
function localize() {
  for (let [id, key] of [
    ["subtitle", "subtitle"],
    ["filter-label", "filter"],
    ["empty", "empty"],
    ["calls-label", "calls"],
    ["tokens-label", "tokens"],
    ["delivery-label", "delivery"],
    ["cost-note", "cost"],
    ["timeline-label", "timeline"],
    ["cancel", "cancel"],
    ["footer", "footer"],
  ])
    text($(id), s()[key]);
  document.documentElement.lang = lang === "pt" ? "pt-BR" : "en";
  renderRuns();
  renderEvents();
  text(
    $("workflows-label"),
    lang === "pt" ? "Pipelines CI/CD" : "CI/CD pipelines",
  );
  if (selected) detail().catch((e) => text($("error"), e.message));
  if (selectedWorkflow)
    workflowDetail().catch((e) => text($("connection"), e.message));
}
async function renderWorkflows() {
  const values = await api("/api/workflows");
  $("workflows").replaceChildren();
  for (const value of values) {
    let button = el("button", null, "run");
    button.append(
      el("strong", value.name),
      el("div", value.repository, "small"),
      el(
        "span",
        pipelineText[lang][value.status] || value.status,
        "tag " + value.status,
      ),
    );
    button.setAttribute("aria-current", value.id === selectedWorkflow);
    button.onclick = () => {
      if (stream) stream.close();
      selected = null;
      selectedWorkflow = value.id;
      $("detail").hidden = true;
      $("empty").hidden = true;
      workflowDetail().catch((e) => text($("connection"), e.message));
    };
    $("workflows").append(button);
  }
}
async function workflowDetail() {
  const identity = selectedWorkflow;
  const value = await api("/api/workflows/" + encodeURIComponent(identity));
  if (identity !== selectedWorkflow) return;
  $("workflow-detail").hidden = false;
  text($("workflow-name"), value.name);
  text(
    $("workflow-freshness"),
    (lang === "pt" ? "Última sincronização: " : "Last synchronized: ") +
      new Date(value.updated_at).toLocaleString(),
  );
  const open = new Set(
    Array.from($("workflow-jobs").querySelectorAll("details[open]")).map(
      (n) => n.dataset.phaseId,
    ),
  );
  $("workflow-jobs").replaceChildren();
  for (const job of value.jobs) {
    $("workflow-jobs").append(
      el(
        "h3",
        job.name + " · " + (pipelineText[lang][job.status] || job.status),
      ),
    );
    const container = el("div");
    $("workflow-jobs").append(container);
    new PipelineView(container).render(
      job.phases.map((p) => ({ ...p, id: job.id + ":" + p.id })),
      lang,
    );
    for (const node of container.querySelectorAll("details"))
      node.open = open.has(node.dataset.phaseId);
    if (job.logs) {
      const logs = el("details", null, "workflow-log");
      logs.dataset.phaseId = job.id + ":logs";
      logs.open = open.has(logs.dataset.phaseId);
      logs.append(
        el(
          "summary",
          lang === "pt" ? "Logs técnicos do job" : "Technical job logs",
        ),
        el("pre", job.logs, "technical-log"),
      );
      $("workflow-jobs").append(logs);
    }
  }
}
$("language").onchange = () => {
  lang = $("language").value;
  localize();
};
$("filter").oninput = renderRuns;
$("cancel").onclick = async () => {
  try {
    await api("/api/runs/" + encodeURIComponent(selected) + "/cancel", {
      method: "POST",
      headers: { "X-Dev-Agent-Kit-Control": "1" },
    });
    text($("error"), s().stop);
    $("cancel").disabled = true;
  } catch (e) {
    text($("error"), e.message);
  }
};
refresh();
setInterval(refresh, 2500);
