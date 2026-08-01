"use strict";

/* ---------- helpers ---------- */

const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function fmtBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fmtDate(iso) {
  if (!iso) return "-";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString("zh-CN", { hour12: false });
}

function truncate(text, max) {
  const value = String(text ?? "");
  return value.length > max ? value.slice(0, max) + "…" : value;
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let detail = `请求失败（HTTP ${response.status}）`;
    try {
      const body = await response.json();
      if (body.detail) detail = String(body.detail);
    } catch {
      /* keep default message */
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  const contentType = response.headers.get("content-type") || "";
  return contentType.includes("application/json") ? response.json() : response.text();
}

function showError(element, message) {
  element.textContent = message;
  element.classList.remove("hidden");
}

function clearError(element) {
  element.textContent = "";
  element.classList.add("hidden");
}

function setBusy(button, busy, busyText = "处理中…") {
  if (!button) return;
  if (busy) {
    button.dataset.originalText = button.textContent;
    button.textContent = busyText;
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
  }
}

/* ---------- tabs ---------- */

const TABS = document.querySelectorAll(".tab");

TABS.forEach((tab) => {
  tab.addEventListener("click", () => {
    TABS.forEach((item) => item.classList.toggle("active", item === tab));
    document.querySelectorAll(".panel").forEach((panel) => {
      panel.classList.toggle("active", panel.id === `panel-${tab.dataset.tab}`);
    });
  });
});

/* ---------- health ---------- */

async function refreshHealth() {
  const dot = $("#healthDot");
  const text = $("#healthText");
  try {
    const data = await api("/health");
    dot.classList.add("ok");
    dot.classList.remove("down");
    text.textContent = `服务正常 · ${data.service}`;
  } catch {
    dot.classList.remove("ok");
    dot.classList.add("down");
    text.textContent = "服务不可用";
  }
}

/* ---------- documents ---------- */

async function renderDocuments() {
  const documents = await api("/documents");
  const body = $("#docBody");
  const empty = $("#docEmpty");
  $("#docCount").textContent = documents.length;

  if (!documents.length) {
    body.innerHTML = "";
    empty.classList.remove("hidden");
    return;
  }

  empty.classList.add("hidden");
  body.innerHTML = documents
    .map(
      (doc) => `
        <tr>
          <td><strong>${escapeHtml(doc.title)}</strong></td>
          <td>${escapeHtml(doc.source_name)}</td>
          <td>${fmtBytes(doc.content_length)}</td>
          <td>${doc.chunk_count}</td>
          <td>${fmtDate(doc.created_at)}</td>
          <td>
            <button class="delete-btn" data-id="${doc.id}"
                    data-title="${escapeHtml(doc.title)}">删除</button>
          </td>
        </tr>
      `
    )
    .join("");

  body.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      if (!window.confirm(`确定删除文档《${button.dataset.title}》？`)) return;
      try {
        await api(`/documents/${button.dataset.id}`, { method: "DELETE" });
        await renderDocuments();
      } catch (error) {
        window.alert(error.message);
      }
    });
  });
}

async function uploadFile(file) {
  clearError($("#uploadError"));
  if (!file) return;
  if (!/\.(md|txt)$/i.test(file.name)) {
    showError($("#uploadError"), "仅支持 .md 或 .txt 文件。");
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  try {
    await api("/documents/upload", { method: "POST", body: formData });
    await renderDocuments();
  } catch (error) {
    showError($("#uploadError"), error.message);
  }
}

function setupUpload() {
  const dropzone = $("#dropzone");
  const fileInput = $("#fileInput");

  fileInput.addEventListener("change", () => {
    uploadFile(fileInput.files[0]);
    fileInput.value = "";
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.add("dragover");
    });
  });
  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });
  dropzone.addEventListener("drop", (event) => {
    const file = event.dataTransfer.files[0];
    uploadFile(file);
  });
}

/* ---------- shared source card renderer ---------- */

function renderSourceCards(container, sources) {
  if (!sources.length) {
    container.innerHTML = `<p class="empty">未检索到相关片段。</p>`;
    return;
  }
  container.innerHTML = sources
    .map((source) => {
      const scorePercent = Math.round((source.score / Math.max(...sources.map((s) => s.score), 1e-9)) * 100);
      return `
        <div class="source">
          <div class="source-head">
            <span class="source-title">${escapeHtml(source.title)}</span>
            <span class="score">
              <span class="score-bar"><span class="score-fill" style="width:${scorePercent}%"></span></span>
              <span class="score-label">${source.score.toFixed(4)}</span>
            </span>
          </div>
          <p class="source-content">${escapeHtml(source.content)}</p>
          <p class="source-meta">
            片段 #${source.chunk_index} · 字符 ${source.char_start}–${source.char_end} ·
            来源 ${escapeHtml(source.source_name)}
          </p>
        </div>
      `;
    })
    .join("");
}

/* ---------- ask ---------- */

async function askQuestion() {
  const input = $("#askInput");
  const question = input.value.trim();
  const button = $("#askBtn");
  clearError($("#askError"));

  if (!question) {
    showError($("#askError"), "请先输入问题。");
    return;
  }

  setBusy(button, true, "回答中…");
  try {
    const data = await api("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: Number($("#askTopK").value) }),
    });
    $("#answerText").textContent = data.answer;
    renderSourceCards($("#askSources"), data.sources);
    $("#askResult").classList.remove("hidden");
  } catch (error) {
    showError($("#askError"), error.message);
  } finally {
    setBusy(button, false);
  }
}

/* ---------- search ---------- */

async function runSearch() {
  const input = $("#searchInput");
  const query = input.value.trim();
  const button = $("#searchBtn");
  clearError($("#searchError"));

  if (!query) {
    showError($("#searchError"), "请输入检索词。");
    return;
  }

  setBusy(button, true, "检索中…");
  try {
    const params = new URLSearchParams({
      q: query,
      top_k: String(Number($("#searchTopK").value)),
    });
    const hits = await api(`/search?${params}`);
    $("#searchMeta").textContent = `共 ${hits.length} 条`;
    renderSourceCards($("#searchHits"), hits);
    $("#searchResult").classList.remove("hidden");
  } catch (error) {
    showError($("#searchError"), error.message);
  } finally {
    setBusy(button, false);
  }
}

/* ---------- evaluation ---------- */

async function runEvaluation() {
  const button = $("#evalBtn");
  clearError($("#evalError"));
  setBusy(button, true, "评测中…");

  try {
    const evalSet = await api("/eval/demo");
    const result = await api("/eval/retrieval", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(evalSet),
    });

    $("#metricRecall").textContent = result.recall_at_k.toFixed(4);
    $("#metricMrr").textContent = result.mrr.toFixed(4);
    $("#metricLatency").textContent = `${result.avg_latency_ms.toFixed(2)}`;

    $("#evalBody").innerHTML = result.details
      .map(
        (detail) => `
          <tr>
            <td>${escapeHtml(detail.question)}</td>
            <td>${escapeHtml(detail.expected)}</td>
            <td>
              <span class="hit-tag ${detail.recalled ? "yes" : "no"}">
                ${detail.recalled ? "命中" : "未命中"}
              </span>
            </td>
            <td>${detail.rr.toFixed(4)}</td>
            <td>${escapeHtml(detail.hits.map((hit) => `${hit.title} (${hit.score.toFixed(3)})`).join("、") || "-")}</td>
            <td>${detail.latency_ms.toFixed(2)} ms</td>
          </tr>
        `
      )
      .join("");
    $("#evalResult").classList.remove("hidden");
  } catch (error) {
    showError($("#evalError"), error.message);
  } finally {
    setBusy(button, false);
  }
}

/* ---------- wire up ---------- */

$("#askBtn").addEventListener("click", askQuestion);
$("#askInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") askQuestion();
});
$("#searchBtn").addEventListener("click", runSearch);
$("#searchInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") runSearch();
});
$("#evalBtn").addEventListener("click", runEvaluation);

setupUpload();
refreshHealth();
renderDocuments().catch((error) => {
  showError($("#uploadError"), error.message);
});
