/* ── State ──────────────────────────────────────────────────────────────────── */
let currentPalette = [];
let history = [];

/* ── DOM refs ───────────────────────────────────────────────────────────────── */
const colorPicker  = document.getElementById("color-picker");
const hexInput     = document.getElementById("hex-input");
const countSlider  = document.getElementById("count-slider");
const countLabel   = document.getElementById("count-label");
const generateBtn  = document.getElementById("generate-btn");
const modeGrid     = document.getElementById("mode-grid");
const paletteStrip = document.getElementById("palette-strip");
const swatchGrid   = document.getElementById("swatch-grid");
const paletteMeta  = document.getElementById("palette-meta");
const exportBar    = document.getElementById("export-bar");
const toast        = document.getElementById("toast");
const historySection = document.getElementById("history-section");
const historyGrid    = document.getElementById("history-grid");

/* ── Helpers ────────────────────────────────────────────────────────────────── */
function getMode() {
  return document.querySelector(".mode-btn.active")?.dataset.mode ?? "random";
}

function isValidHex(v) {
  return /^#[0-9a-fA-F]{6}$/.test(v);
}

function contrastColor(hex) {
  const [r, g, b] = [hex.slice(1,3), hex.slice(3,5), hex.slice(5,7)].map(h => parseInt(h, 16));
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.55 ? "#111" : "#fff";
}

function showToast(msg = "✓ Copied!") {
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2000);
}

async function copyText(text) {
  try { await navigator.clipboard.writeText(text); } catch { /* fallback */ }
  showToast();
}

/* ── Color input sync ───────────────────────────────────────────────────────── */
colorPicker.addEventListener("input", () => {
  hexInput.value = colorPicker.value;
});

hexInput.addEventListener("input", () => {
  const v = hexInput.value.trim();
  if (isValidHex(v)) colorPicker.value = v;
});

/* ── Count slider ───────────────────────────────────────────────────────────── */
countSlider.addEventListener("input", () => {
  countLabel.textContent = countSlider.value;
});

/* ── Mode buttons ───────────────────────────────────────────────────────────── */
modeGrid.addEventListener("click", (e) => {
  const btn = e.target.closest(".mode-btn");
  if (!btn) return;
  document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
});

/* ── Swatch card builder ────────────────────────────────────────────────────── */
function buildCard(swatch, index) {
  const card = document.createElement("div");
  card.className = "swatch-card";
  card.style.animationDelay = `${index * 60}ms`;

  const fg = contrastColor(swatch.hex);

  card.innerHTML = `
    <div class="swatch-block" style="background:${swatch.hex}"></div>
    <div class="swatch-info">
      <div class="swatch-name">${swatch.name}</div>
      <div class="swatch-hex">${swatch.hex}</div>
      <div class="swatch-values">
        RGB ${swatch.rgb.r}, ${swatch.rgb.g}, ${swatch.rgb.b}<br>
        HSL ${swatch.hsl.h}° ${swatch.hsl.s}% ${swatch.hsl.l}%
      </div>
    </div>
  `;

  card.addEventListener("click", () => {
    copyText(swatch.hex);
    card.classList.remove("copied");
    void card.offsetWidth;
    card.classList.add("copied");
  });

  return card;
}

/* ── Strip builder ──────────────────────────────────────────────────────────── */
function buildStrip(palette) {
  paletteStrip.innerHTML = "";
  palette.forEach(sw => {
    const seg = document.createElement("div");
    seg.className = "strip-segment";
    seg.style.background = sw.hex;
    seg.innerHTML = `<span class="strip-tip">${sw.hex}</span>`;
    seg.addEventListener("click", () => copyText(sw.hex));
    paletteStrip.appendChild(seg);
  });
}

/* ── History ────────────────────────────────────────────────────────────────── */
function pushHistory(palette, mode) {
  if (history.length >= 8) history.pop();
  history.unshift({ palette: [...palette], mode });
  renderHistory();
  historySection.style.display = "block";
}

function renderHistory() {
  historyGrid.innerHTML = "";
  history.forEach(({ palette, mode }) => {
    const row = document.createElement("div");
    row.className = "history-row";

    const mini = document.createElement("div");
    mini.className = "history-strip-mini";
    palette.forEach(sw => {
      const s = document.createElement("span");
      s.style.background = sw.hex;
      mini.appendChild(s);
    });

    const label = document.createElement("span");
    label.className = "history-label";
    label.textContent = mode;

    row.append(mini, label);
    row.addEventListener("click", () => renderPalette(palette, mode, false));
    historyGrid.appendChild(row);
  });
}

/* ── Main render ────────────────────────────────────────────────────────────── */
function renderPalette(palette, mode, saveHistory = true) {
  currentPalette = palette;

  paletteMeta.textContent = `${palette.length} swatches · ${mode}`;

  buildStrip(palette);

  swatchGrid.innerHTML = "";
  palette.forEach((sw, i) => swatchGrid.appendChild(buildCard(sw, i)));

  exportBar.style.display = "flex";

  if (saveHistory) pushHistory(palette, mode);
}

/* ── Generate ───────────────────────────────────────────────────────────────── */
async function generate() {
  const mode  = getMode();
  const color = hexInput.value.trim();
  const count = parseInt(countSlider.value);

  if (!isValidHex(color) && mode !== "random") {
    hexInput.style.borderColor = "tomato";
    setTimeout(() => hexInput.style.borderColor = "", 1000);
    return;
  }

  generateBtn.disabled = true;
  generateBtn.textContent = "Forging…";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode, color, count }),
    });
    const data = await res.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    renderPalette(data.palette, data.mode);
  } catch (err) {
    alert("Request failed: " + err.message);
  } finally {
    generateBtn.disabled = false;
    generateBtn.innerHTML = `<span class="btn-icon">⬡</span> Generate Palette`;
  }
}

/* ── Export buttons ─────────────────────────────────────────────────────────── */
document.getElementById("copy-css-btn").addEventListener("click", () => {
  const css = currentPalette.map((sw, i) =>
    `  --color-${i + 1}: ${sw.hex};`
  ).join("\n");
  copyText(`:root {\n${css}\n}`);
});

document.getElementById("copy-json-btn").addEventListener("click", () => {
  copyText(JSON.stringify(currentPalette, null, 2));
});

document.getElementById("copy-hex-btn").addEventListener("click", () => {
  copyText(currentPalette.map(sw => sw.hex).join(", "));
});

/* ── Init ───────────────────────────────────────────────────────────────────── */
generateBtn.addEventListener("click", generate);

// Keyboard shortcut: Space or Enter to generate
document.addEventListener("keydown", (e) => {
  if ((e.key === " " || e.key === "Enter") && document.activeElement === document.body) {
    e.preventDefault();
    generate();
  }
});

// Generate on load
generate();
