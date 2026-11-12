"use strict";
const el = id => document.getElementById(id);
let csrf = null, polling = null, active = false;
async function request(path, body) {
  const response = await fetch(path, { method: body === undefined ? "GET" : "POST", credentials: "same-origin", cache: "no-store", redirect: "error",
    headers: body === undefined ? {} : { "Content-Type": "application/json", "X-Demo-CSRF": csrf },
    body: body === undefined ? undefined : JSON.stringify(body) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error?.message || "The demo could not complete this request.");
  return data;
}
function error(message) { el("error").hidden = !message; el("error").textContent = message || ""; }
function fact(title, value) {
  const row = document.createElement("div"), dt = document.createElement("dt"), dd = document.createElement("dd");
  dt.textContent = title; dd.textContent = String(value); row.append(dt, dd); el("facts").append(row);
}
function link(title, href) {
  const a = document.createElement("a"); a.className = "btn btn-secondary"; a.textContent = title; a.href = href; el("result-links").append(a);
}
function render(job) {
  active = job?.state === "running";
  const uncertain = job?.state === "uncertain";
  el("run").disabled = !csrf || active || uncertain;
  el("reset").disabled = !job || active || uncertain;
  for (const input of el("samples").querySelectorAll("input")) input.disabled = active || uncertain;
  if (!job) { el("status").textContent = "Ready. The next run invokes the native production. Inspect the returned execution mode; a fresh model answer is not assumed."; el("result").hidden = true; return; }
  if (active) { el("status").textContent = "Investigation admitted. Waiting for the native result; no tool progress is simulated here."; return; }
  if (polling) { clearInterval(polling); polling = null; }
  if (uncertain) { el("status").textContent = "Native completion is unconfirmed. The attempt is retained and further investigations are blocked for reconciliation."; return; }
  for (const input of el("samples").querySelectorAll("input")) input.checked = input.value === job.scenario;
  const record = job.result, agent = record?.agent || {};
  if (!record) { error("No persisted native result is available."); return; }
  el("result").hidden = false;
  el("result-heading").textContent = ({ QUARANTINED: "Held before delivery", DELIVERED: "Delivered to the simulator", REVIEW: "Held for human review" })[record.routing] || record.routing;
  el("reason").textContent = Array.isArray(record.policy?.reasons) ? record.policy.reasons.join(" ") : "Inspect the recorded policy checks in the workbench.";
  el("facts").replaceChildren(); el("result-links").replaceChildren();
  fact("Native case", record.id); fact("Simulator deliveries", record.delivery_count);
  fact("Agent outcome", agent.status || "Unavailable");
  const execution = agent.execution_mode === "recorded-replay" && agent.status === "returned"
    ? "Recorded agent proposal replayed through native IRIS AI Hub; no fresh inference"
    : agent.execution_mode === "live" && agent.model_invoked === true && agent.status === "returned"
      ? "Native AI Hub returned a live model answer"
      : "Inspect the native invocation status; a completed answer is not assumed";
  fact("Execution", execution);
  if (agent.model) fact("Model", agent.model);
  if (typeof agent.elapsed_ms === "number") fact("Native investigation time", (agent.elapsed_ms / 1000).toFixed(2)+" seconds");
  if (typeof job.finished === "number") fact("Gateway wall time", (job.finished-job.created).toFixed(2)+" seconds");
  if (/^[A-Fa-f0-9-]{36}$/.test(record.id)) link("Inspect this case", "/#investigations/"+record.id);
  if (/^\d+$/.test(record.trace_id)) link("Open native Visual Trace", "/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID="+record.trace_id+"&PRINTABLE=1&PAGE=1");
  link("Production status", "/#health");
  el("sources").textContent = JSON.stringify({ message: record.message, references: record.references }, null, 2);
  el("status").textContent = "The persisted native result is ready. Inspect the evidence before drawing a conclusion.";
}
async function refresh() {
  const data = await request("/demo/status"); csrf = data.csrf; render(data.job);
  el("limits").textContent = `${data.limits.runs_per_address} investigations per address in ${data.limits.window_seconds/60} minutes; ${data.limits.trial_runs} total trial investigations. Read-only inspection remains available.`;
  el("expires").textContent = "Trial closes automatically: "+new Date(data.expires_at*1000).toLocaleString()+" ("+new Date(data.expires_at*1000).toISOString()+").";
  if (active && !polling) polling = setInterval(() => refresh().catch(e => { error(e.message); clearInterval(polling); polling = null; }), 2000);
}
el("run").addEventListener("click", async () => {
  if (active || !csrf) return;
  error(null); el("run").disabled = true;
  try {
    const scenario = document.querySelector('input[name="scenario"]:checked').value;
    const data = await request("/demo/run", { scenario, request_id: crypto.randomUUID() }); render(data.job); await refresh();
  } catch (e) { error(e.message); el("run").disabled = false; }
});
el("reset").addEventListener("click", async () => {
  error(null);
  try { await request("/demo/reset", {}); await refresh(); } catch (e) { error(e.message); }
});
el("access").addEventListener("click", async () => {
  error(null);
  try {
    const data = await request("/demo/access"); el("viewer-name").value = data.username; el("viewer-password").value = data.password;
    el("viewer-access").hidden = false; el("access").setAttribute("aria-expanded", "true"); el("viewer-name").focus();
  } catch (e) { error(e.message); }
});
el("show-password").addEventListener("click", () => {
  const show = el("viewer-password").type === "password"; el("viewer-password").type = show ? "text" : "password";
  el("show-password").textContent = show ? "Hide demo password" : "Show demo password";
});
refresh().catch(e => { error(e.message); el("status").textContent = "The replay demo could not be reached. No investigation was started."; });
