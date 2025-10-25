// static/mindfield.js

document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("constellation");
  const ctx = canvas.getContext("2d");
  const queryInput = document.getElementById("query");
  const submitBtn = document.getElementById("submit");
  const status = document.getElementById("status");
  const output = document.getElementById("output");

  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  async function runQuery() {
    const q = queryInput.value.trim();
    if (!q) return;
    status.textContent = "⟳ querying...";
    output.textContent = "";

    try {
      const res = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q }),
      });
      const data = await res.json();

      if (data.output) {
        // --- NEW: Textual mode rendering ---
        status.textContent = "formatting bridge output...";
        renderTextOutput(data.output);
        status.textContent = "✅ bridge complete";
      } else {
        // --- Constellation mode (fallback) ---
        status.textContent = "rendering constellation...";
        drawConstellation(data);
        status.textContent = "✅ complete";
      }
    } catch (err) {
      console.error(err);
      status.textContent = "⚠️ error in bridge";
      output.textContent = "Bridge error — no geometry returned.";
    }
  }

  /**
   * NEW: Parses the raw text output from the server
   * and renders it as structured HTML.
   */
  function renderTextOutput(text) {
    const lines = text.split('\n');
    let html = '';

    lines.forEach(line => {
      if (line.trim() === "") return; // Skip empty lines

      if (line.startsWith('🧭')) {
        html += `<span class="layer-title orientation">${line}</span>`;
      } else if (line.startsWith('🌿')) {
        html += `<span class="layer-title texture">${line}</span>`;
      } else if (line.startsWith('  •')) {
        html += `<span class="list-item">${line}</span>`;
      } else if (line.startsWith('    →')) {
        html += `<span class="text-preview">${line}</span>`;
      } else if (line.startsWith('✅')) {
        // You can style the 'complete' messages differently if you want
        html += `<span style="color: limegreen;">${line}</span>\n`;
      } else {
        html += `${line}\n`; // Add other lines as-is
      }
    });

    output.innerHTML = html;
  }

  submitBtn.addEventListener("click", runQuery);
  queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runQuery();
  });

  // --- Constellation visual layer ---
  // (This function is unchanged)
  function drawConstellation(data) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const { orientation = [], texture = [] } = data;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    const mapX = (x) => cx + x * (canvas.width * 0.35);
    const mapY = (y) => cy + y * (canvas.height * 0.35);

    // draw resonance links
    texture.forEach((t, i) => {
      const o = orientation[i % orientation.length];
      ctx.beginPath();
      ctx.moveTo(mapX(o.x), mapY(o.y));
      ctx.lineTo(mapX(t.x), mapY(t.y));
      ctx.strokeStyle = "rgba(255,255,255,0.08)";
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // draw the compasses and fragments
    orientation.forEach((n) => drawNode(n, "gold"));
    texture.forEach((n) => drawNode(n, "cyan"));

    function drawNode(n, color) {
      ctx.beginPath();
      ctx.arc(mapX(n.x), mapY(n.y), 5, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.shadowColor = color;
      ctx.shadowBlur = 12;
      ctx.fill();

      ctx.font = "12px monospace";
      ctx.fillStyle = "rgba(255,255,255,0.65)";
      const label = n.title || n.excerpt?.slice(0, 48) || n.id;
      ctx.fillText(label, mapX(n.x) + 10, mapY(n.y) + 3);
    }
  }
});