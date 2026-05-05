const form = document.getElementById("process-form");
const fileInput = document.getElementById("file-input");
const fileName = document.getElementById("file-name");
const resultEmpty = document.getElementById("result-empty");
const resultContent = document.getElementById("result-content");
const resultAlgorithm = document.getElementById("result-algorithm");
const resultOperation = document.getElementById("result-operation");
const metricGrid = document.getElementById("metric-grid");
const efficiencyList = document.getElementById("efficiency-list");
const downloadArea = document.getElementById("download-area");
const comparisonLink = document.getElementById("comparison-link");

// Bonus elements
const bonusSection = document.getElementById("bonus-section");
const errorProbSlider = document.getElementById("error-prob-slider");
const errorProbValue = document.getElementById("error-prob-value");
const simulateBtn = document.getElementById("simulate-channel-btn");
const channelResult = document.getElementById("channel-result");
const channelStatus = document.getElementById("channel-status");
const flipsCount = document.getElementById("flips-count");
const correctedCount = document.getElementById("corrected-count");

// Preview elements
const fileContentDisplay = document.getElementById("file-content-display");
const previewTitle = document.getElementById("preview-title");

let currentCompressedFilePath = "";

if (fileInput) {
  fileInput.addEventListener("change", () => {
    const currentFile = fileInput.files[0];
    fileName.textContent = currentFile ? currentFile.name : "No file selected";
  });
}

if (errorProbSlider && errorProbValue) {
  errorProbSlider.addEventListener("input", () => {
    const prob = errorProbSlider.value;
    errorProbValue.textContent = `${(prob * 100).toFixed(1)}% (${prob})`;
  });
}

function createMetricCard(label, value) {
  const card = document.createElement("div");
  card.className = "metric-card";
  card.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
  return card;
}

function createKeyValueItem(key, value) {
  const item = document.createElement("div");
  item.className = "key-value-item";
  item.innerHTML = `<strong>${key}</strong><div>${value}</div>`;
  return item;
}

function renderDownload(download) {
  downloadArea.innerHTML = "";
  const anchor = document.createElement("a");
  anchor.className = "download-chip";
  anchor.href = `/download?path=${encodeURIComponent(download.path)}`;
  anchor.innerHTML = `<div><div>${download.filename}</div><small>${download.relative_path}</small></div>`;
  downloadArea.appendChild(anchor);
}

function renderResult(primary, comparisonUrl) {
  resultEmpty.classList.add("hidden");
  resultContent.classList.remove("hidden");
  resultAlgorithm.textContent = primary.algorithm;
  resultOperation.textContent = primary.operation;

  metricGrid.innerHTML = "";
  Object.entries(primary.stats).forEach(([key, value]) => {
    metricGrid.appendChild(createMetricCard(key, value));
  });

  efficiencyList.innerHTML = "";
  Object.entries(primary.data_structure_efficiency).forEach(([key, value]) => {
    efficiencyList.appendChild(createKeyValueItem(key, value));
  });

  renderDownload(primary.download);
  comparisonLink.href = comparisonUrl;

  // Show Modal with Preview
  showFilePreview(primary);

  // Bonus handling
  if (primary.operation === "compress" && bonusSection) {
    currentCompressedFilePath = primary.download.path;
    bonusSection.classList.remove("hidden");
    if (channelResult) channelResult.classList.add("hidden");
  } else if (bonusSection) {
    bonusSection.classList.add("hidden");
  }
}

async function showFilePreview(primary) {
  if (previewTitle) previewTitle.textContent = primary.operation === "compress" ? "Compressed Content View" : "Decompressed Content View";
  if (fileContentDisplay) fileContentDisplay.textContent = "Loading preview...";

  try {
    const response = await fetch(`/download?path=${encodeURIComponent(primary.download.path)}`);
    const blob = await response.blob();
    const buffer = await blob.arrayBuffer();
    const view = new Uint8Array(buffer);
    
    let isBinary = false;
    for (let i = 0; i < Math.min(view.length, 1024); i++) {
      if (view[i] === 0) { isBinary = true; break; }
    }

    if (isBinary) {
      if (fileContentDisplay) fileContentDisplay.textContent = "[Binary Data - Preview not available]";
    } else {
      const text = new TextDecoder().decode(buffer);
      if (fileContentDisplay) {
        fileContentDisplay.textContent = text.length > 5000 ? text.substring(0, 5000) + "\n\n... [Content Truncated]" : text;
      }
    }
  } catch (err) {
    if (fileContentDisplay) fileContentDisplay.textContent = "Error: " + err.message;
  }
}

if (simulateBtn) {
  simulateBtn.addEventListener("click", async () => {
    simulateBtn.disabled = true;
    simulateBtn.textContent = "Simulating...";
    
    try {
      const response = await fetch("/api/simulate_channel", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_path: currentCompressedFilePath,
          error_probability: parseFloat(errorProbSlider.value)
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Simulation failed");

      if (channelResult) channelResult.classList.remove("hidden");
      if (channelStatus) {
        channelStatus.textContent = data.stats.integrity_maintained ? "RECOVERED SUCCESSFULLY" : "RECOVERY FAILED";
        channelStatus.style.color = data.stats.integrity_maintained ? "#9bd2b0" : "#ff6b6b";
      }
      if (flipsCount) flipsCount.textContent = data.stats.actual_flips;
      if (correctedCount) correctedCount.textContent = data.stats.corrected_errors;
      
    } catch (error) {
      alert(error.message);
    } finally {
      simulateBtn.disabled = false;
      simulateBtn.textContent = "Simulate Noisy Channel";
    }
  });
}

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const submitButton = form.querySelector("button[type='submit']");
    submitButton.disabled = true;
    submitButton.textContent = "Processing...";

    try {
      const response = await fetch("/api/process", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Processing failed");
      }

      renderResult(data.primary, data.comparison_url);
    } catch (error) {
      alert(error.message);
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Process File";
    }
  });
}
