function formatValue(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) ? value : value.toFixed(4);
  }
  return value ?? "-";
}

function formatLabel(value) {
  return String(value || "-")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function createMetricChip(label, value) {
  return `
    <div class="metric-chip">
      <span>${label}</span>
      <strong>${formatValue(value)}</strong>
    </div>
  `;
}

function buildStructureNote(dataStructureEfficiency) {
  const entries = Object.entries(dataStructureEfficiency || {});

  if (!entries.length) {
    return "Structured analysis data is available for this algorithm run.";
  }

  return entries
    .slice(0, 2)
    .map(([key, value]) => `${formatLabel(key)}: ${value}`)
    .join(" ");
}

function buildAlgorithmPanel(result, sourceFile) {
  const previewCode = result.preview?.compressed_code ?? "-";
  const previewLow = result.preview?.final_low;
  const previewHigh = result.preview?.final_high;
  const codePreview = Array.isArray(result.preview?.codes) && result.preview.codes.length
    ? result.preview.codes.slice(0, 8).join(", ")
    : "Not applicable";
  const codeTablePreview = Array.isArray(result.preview?.code_table) && result.preview.code_table.length
    ? result.preview.code_table.slice(0, 4).map((row) => `${row.symbol}: ${row.code}`).join(" | ")
    : "Not applicable";
  const previewText = codePreview !== "Not applicable" ? codePreview : codeTablePreview;
  const downloadPath = result.download?.path || "";

  return `
    <article class="algorithm-overview-card">
      <div class="algorithm-overview-top">
        <div>
          <span class="mini-label">${result.algorithm}</span>
          <h2>${result.algorithm}</h2>
          <p>${result.algorithm} was executed on the same source context so the comparison stays fair and directly readable.</p>
        </div>
        <div class="algorithm-status">
          <span>Workflow</span>
          <strong>${formatLabel(result.operation)}</strong>
        </div>
      </div>

      <div class="overview-meta-grid">
        <div class="overview-meta-item">
          <span>Source File</span>
          <strong>${sourceFile}</strong>
        </div>
        <div class="overview-meta-item">
          <span>File Type</span>
          <strong>${formatLabel(result.file_type)}</strong>
        </div>
        <div class="overview-meta-item">
          <span>Output File</span>
          <strong>${result.download?.filename || "-"}</strong>
        </div>
        <div class="overview-meta-item">
          <span>Saved Path</span>
          <strong>${result.download?.relative_path || "-"}</strong>
        </div>
      </div>

      <div class="algorithm-chip-grid">
        ${createMetricChip("Compression Ratio", result.stats.compression_ratio)}
        ${createMetricChip("Compressed Size", result.stats.compressed_size_bytes)}
        ${createMetricChip("Execution Time", result.stats.execution_time_seconds)}
        ${createMetricChip("Memory Usage", result.stats.memory_usage_bytes)}
        ${createMetricChip("Entropy", result.stats.entropy_bits_per_symbol)}
        ${createMetricChip("Compression Speed", result.stats.compression_speed_bytes_per_second)}
      </div>

      <div class="algorithm-detail-grid">
        <div class="algorithm-detail-block">
          <span class="detail-title">Compression Preview</span>
          <p>${previewText}</p>
        </div>
        <div class="algorithm-detail-block">
          <span class="detail-title">Range Summary</span>
          <p>Low: ${formatValue(previewLow)} | High: ${formatValue(previewHigh)} | Code: ${formatValue(previewCode)}</p>
        </div>
        <div class="algorithm-detail-block">
          <span class="detail-title">Structure Note</span>
          <p>${buildStructureNote(result.data_structure_efficiency)}</p>
        </div>
      </div>

      ${downloadPath ? `
        <div class="overview-actions">
          <a class="secondary-button compact" href="/download?path=${encodeURIComponent(downloadPath)}">Download Output</a>
        </div>
      ` : ""}
    </article>
  `;
}

function buildBarRow(label, primaryValue, secondaryValue, higherIsBetter = true) {
  const row = document.createElement("div");
  row.className = "bar-row";

  const maxValue = Math.max(primaryValue || 0, secondaryValue || 0, 1);
  const primaryWidth = ((primaryValue || 0) / maxValue) * 100;
  const secondaryWidth = ((secondaryValue || 0) / maxValue) * 100;

  row.innerHTML = `
    <div class="bar-head">
      <span>${label}</span>
      <span>${higherIsBetter ? "Higher is stronger" : "Lower is stronger"}</span>
    </div>
    <div class="bar-track"><div class="bar-fill" style="width:${primaryWidth}%"></div></div>
    <div class="bar-head">
      <span>${formatValue(primaryValue)}</span>
      <span>${formatValue(secondaryValue)}</span>
    </div>
    <div class="bar-track"><div class="bar-fill" style="width:${secondaryWidth}%; opacity:0.72"></div></div>
  `;

  return row;
}

function buildMetricRow(label, primaryValue, secondaryValue) {
  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${label}</td>
    <td>${formatValue(primaryValue)}</td>
    <td>${formatValue(secondaryValue)}</td>
  `;
  return row;
}

async function loadComparison() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  const root = document.getElementById("comparison-root");

  if (!id) {
    root.innerHTML = '<div class="comparison-card"><p>Missing comparison identifier.</p></div>';
    return;
  }

  const response = await fetch(`/api/comparison?id=${encodeURIComponent(id)}`);
  const data = await response.json();

  if (!response.ok) {
    root.innerHTML = `<div class="comparison-card"><p>${data.error || "Unable to load comparison."}</p></div>`;
    return;
  }

  const primary = data.primary;
  const secondary = data.secondary;

  root.innerHTML = `
    <section class="comparison-card comparison-context-card">
      <span class="mini-label">Reading Notes</span>
      <h1>How View Comparison works</h1>
      <div class="comparison-notes comparison-notes-wide">
        <div class="note-item">
          <strong>1. Primary run</strong>
          <p>The algorithm you selected first is executed and its output file is saved.</p>
        </div>
        <div class="note-item">
          <strong>2. Matching run</strong>
          <p>The other algorithm is then executed on the same source context in the background.</p>
        </div>
        <div class="note-item">
          <strong>3. Unified metrics</strong>
          <p>Both runs are measured with the same metrics so the table and graphs stay directly comparable.</p>
        </div>
        <div class="note-item">
          <strong>4. Stored snapshot</strong>
          <p>The comparison result is saved as a dedicated snapshot, so reopening the page shows the same pair again.</p>
        </div>
      </div>
    </section>

    <section class="algorithm-overview-grid">
      ${buildAlgorithmPanel(primary, data.source_file)}
      ${buildAlgorithmPanel(secondary, data.source_file)}
    </section>

    <section class="comparison-stage comparison-stage-single">
      <div class="comparison-card">
        <span class="mini-label">Visual Analysis</span>
        <h2>Metric Graphs</h2>
        <p>Each graph compares the same metric for both algorithms. The visual length helps scanning, while the exact values stay visible under every bar.</p>
        <div class="chart-legend">
          <div class="legend-chip"><span class="legend-swatch primary-swatch"></span>${primary.algorithm}</div>
          <div class="legend-chip"><span class="legend-swatch secondary-swatch"></span>${secondary.algorithm}</div>
        </div>
        <div id="chart-stack" class="chart-stack"></div>
      </div>
    </section>
    <section class="comparison-card">
      <span class="mini-label">Comparison Table</span>
      <h2>Detailed metrics</h2>
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>${primary.algorithm}</th>
            <th>${secondary.algorithm}</th>
          </tr>
        </thead>
        <tbody id="comparison-table-body"></tbody>
      </table>
    </section>
  `;

  const chartStack = document.getElementById("chart-stack");
  chartStack.appendChild(buildBarRow("Compression Ratio", primary.stats.compression_ratio, secondary.stats.compression_ratio, true));
  chartStack.appendChild(buildBarRow("Compressed Size (bytes)", primary.stats.compressed_size_bytes, secondary.stats.compressed_size_bytes, false));
  chartStack.appendChild(buildBarRow("Execution Time (seconds)", primary.stats.execution_time_seconds, secondary.stats.execution_time_seconds, false));
  chartStack.appendChild(buildBarRow("Memory Usage (bytes)", primary.stats.memory_usage_bytes, secondary.stats.memory_usage_bytes, false));

  const tableBody = document.getElementById("comparison-table-body");
  [
    "original_size_bytes",
    "compressed_size_bytes",
    "compression_ratio",
    "execution_time_seconds",
    "compression_speed_bytes_per_second",
    "entropy_bits_per_symbol",
    "memory_usage_bytes",
    "saved_compressed_file_size_bytes",
  ].forEach((key) => {
    tableBody.appendChild(buildMetricRow(formatLabel(key), primary.stats[key], secondary.stats[key]));
  });
}

loadComparison();
