/**
 * Sentinel AI dashboard — talks to Flask /api/analyze
 */
const API_BASE = "";

const $ = (id) => document.getElementById(id);

const SAMPLE_THREAT =
  "GET /admin?id=1' UNION SELECT password FROM users-- HTTP/1.1\n" +
  "User-Agent: sqlmap/1.7.2#stable (http://sqlmap.org)\n" +
  "Referer: https://evil.example/callback?data=PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==";

function showToast(message) {
  const el = $("toast");
  el.textContent = message;
  el.hidden = false;
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => {
    el.hidden = true;
  }, 5000);
}

async function checkHealth() {
  const pill = $("apiStatus");
  pill.dataset.state = "checking";
  pill.textContent = "API: checking…";
  try {
    const r = await authFetch(`${API_BASE}/api/health`, { method: "GET" });
    if (!r.ok) throw new Error(String(r.status));
    pill.dataset.state = "ok";
    pill.textContent = "API: connected";
  } catch {
    pill.dataset.state = "error";
    pill.textContent = "API: offline — start backend";
  }
}

function saveHistory(entry) {
  try {
    const key = "sentinel_history";
    const raw = localStorage.getItem(key);
    const list = raw ? JSON.parse(raw) : [];
    list.unshift(entry);
    localStorage.setItem(key, JSON.stringify(list.slice(0, 20)));
    renderHistory();
  } catch {
    /* ignore */
  }
}

function loadHistory() {
  try {
    const raw = localStorage.getItem("sentinel_history");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function renderHistory() {
  const ul = $("historyList");
  ul.innerHTML = "";
  const list = loadHistory();
  if (!list.length) {
    const li = document.createElement("li");
    li.textContent = "No runs yet.";
    li.style.cursor = "default";
    li.style.borderStyle = "dashed";
    ul.appendChild(li);
    return;
  }
  list.forEach((h) => {
    const li = document.createElement("li");
    const preview = (h.preview || "").slice(0, 72);
    li.innerHTML = `<div>${escapeHtml(preview)}${preview.length >= 72 ? "…" : ""}</div>
      <div class="history-meta"><span>score ${h.score}</span><span>${escapeHtml(h.severity)}</span></div>`;
    li.addEventListener("click", () => {
      $("payload").value = h.fullText || h.preview || "";
      $("analysisType").value = h.type || "auto";
    });
    ul.appendChild(li);
  });
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function renderResult(res) {
  const panel = $("resultsPanel");
  panel.hidden = false;

  const score = res.threat_score ?? 0;
  $("scoreValue").textContent = String(score);
  $("scoreRing").style.setProperty("--score", String(score));

  const badge = $("severityBadge");
  const sev = (res.severity || "minimal").toLowerCase();
  badge.textContent = sev;
  badge.className = "severity-badge " + sev;

  const ind = $("indicatorList");
  ind.innerHTML = "";
  (res.indicators || []).forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    ind.appendChild(li);
  });
  if (!ind.children.length) {
    const li = document.createElement("li");
    li.textContent = "No strong indicators — low signal in this sample.";
    ind.appendChild(li);
  }

  const tbody = $("contribBody");
  tbody.innerHTML = "";
  (res.feature_contributions || []).forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${escapeHtml(row.feature)}</td><td>${row.activation}</td><td>${row.weight}</td><td>${row.contribution}</td>`;
    tbody.appendChild(tr);
  });

  const mit = $("mitigationList");
  mit.innerHTML = "";
  (res.mitigations || []).forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    mit.appendChild(li);
  });

  $("modelId").textContent = res.model ? `Model: ${res.model}` : "";
}

async function runAnalyze() {
  const text = $("payload").value.trim();
  const type = $("analysisType").value;
  if (!text) {
    showToast("Enter text to analyze.");
    return;
  }
  try {
    const r = await authFetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, type }),
    });
    const data = await r.json();
    if (!r.ok || !data.success) {
      throw new Error(data.error || r.statusText);
    }
    const res = data.result;
    renderResult(res);
    saveHistory({
      preview: text.split("\n")[0],
      fullText: text,
      type,
      score: res.threat_score,
      severity: res.severity,
      at: new Date().toISOString(),
    });
  } catch (e) {
    showToast("Request failed: " + (e.message || "unknown") + ". Is the backend running?");
  }
}

$("btnAnalyze").addEventListener("click", runAnalyze);
$("btnSample").addEventListener("click", () => {
  $("payload").value = SAMPLE_THREAT;
  $("analysisType").value = "log";
});
$("btnClear").addEventListener("click", () => {
  $("payload").value = "";
  $("resultsPanel").hidden = true;
});

document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  renderHistory();
  setInterval(checkHealth, 15000);
});

// Chatbot logic has been migrated securely to /static/js/chat_widget.js
