(() => {
  const $ = (sel) => document.querySelector(sel);

  const API_URL = "/api/dashboard";

  const elUpdatedAt = $("#updatedAt");
  const elStatusText = $("#statusText");

  const elKpiEvents = $("#kpiEvents");
  const elKpiAcl = $("#kpiAcl");
  const elKpiDdos = $("#kpiDdos");
  const elKpiAllowed = $("#kpiAllowed");

  const canvas = $("#chart");
  const tooltip = $("#chartTooltip");
  const eventsBody = $("#eventsBody");

  const MAX_POINTS = 120;

  const series = {
    labels: [],
    flows: [],
    acl: [],
    ddos: [],
    allowed: [],
  };

  function setStatus(text) {
    if (elStatusText) elStatusText.textContent = text;
  }

  async function fetchJsonSafe(url) {
    const r = await fetch(url, { cache: "no-store" });
    const text = await r.text();

    if (!r.ok) {
      throw new Error(`HTTP ${r.status} ${r.statusText}`);
    }
    if (!text || !text.trim()) return null;

    try {
      return JSON.parse(text);
    } catch {
      throw new Error("Invalid JSON (empty or truncated response)");
    }
  }

  function fmtIso(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return isNaN(d.getTime()) ? String(iso) : d.toLocaleString();
  }

  function clampToMax() {
    for (const k of Object.keys(series)) {
      if (series[k].length > MAX_POINTS) series[k] = series[k].slice(-MAX_POINTS);
    }
  }

  // ---- Chart drawing ----
  function ensureHiDpi(c) {
    const dpr = window.devicePixelRatio || 1;
    const cssW = c.clientWidth || 800;
    const cssH = c.clientHeight || 320;
    c.width = Math.floor(cssW * dpr);
    c.height = Math.floor(cssH * dpr);
    const ctx = c.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx, W: cssW, H: cssH };
  }

  function computeScale(allValues) {
    let minY = Math.min(...allValues);
    let maxY = Math.max(...allValues);

    const minRange = 6;
    let range = maxY - minY;
    if (!isFinite(range)) range = 0;

    if (range < minRange) {
      const mid = (maxY + minY) / 2;
      minY = mid - minRange / 2;
      maxY = mid + minRange / 2;
    } else {
      const padding = range * 0.20;
      minY -= padding;
      maxY += padding;
    }
    return { minY, maxY, range: (maxY - minY) || 1 };
  }

  function drawChart() {
    if (!canvas) return;

    const { ctx, W, H } = ensureHiDpi(canvas);
    const pad = 28;

    ctx.clearRect(0, 0, W, H);

    // frame
    ctx.strokeStyle = "rgba(255,255,255,0.12)";
    ctx.strokeRect(0.5, 0.5, W - 1, H - 1);

    const n = series.labels.length;
    if (n < 2) return;

    const all = [
      ...series.flows,
      ...series.acl,
      ...series.ddos,
      ...series.allowed,
    ].map((v) => Number(v || 0));

    const { minY, range } = computeScale(all);

    const plotW = W - pad * 2;
    const plotH = H - pad * 2;

    const xAt = (i) => pad + (i / (n - 1)) * plotW;
    const yAt = (v) => pad + (1 - (Number(v || 0) - minY) / range) * plotH;

    // grid
    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.lineWidth = 1;
    for (let g = 0; g <= 5; g++) {
      const y = pad + (g / 5) * plotH;
      ctx.beginPath();
      ctx.moveTo(pad, y);
      ctx.lineTo(pad + plotW, y);
      ctx.stroke();
    }

    // helper: draw one line
    function line(values, strokeStyle) {
      ctx.strokeStyle = strokeStyle;
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        const x = xAt(i);
        const y = yAt(values[i]);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }

    line(series.flows,   "rgba(74,163,255,0.95)"); 
    line(series.acl,     "rgba(255,93,93,0.95)");   
    line(series.ddos,    "rgba(255,204,102,0.95)");  
    line(series.allowed, "rgba(122,255,180,0.90)"); 
  }

  // ---- Tooltip ----
  function bindTooltip() {
    if (!canvas || !tooltip) return;

    function hide() {
      tooltip.style.display = "none";
    }

    function onMove(ev) {
      const rect = canvas.getBoundingClientRect();
      const x = ev.clientX - rect.left;
      const y = ev.clientY - rect.top;

      const pad = 28;
      const plotW = rect.width - pad * 2;
      const n = series.labels.length;
      if (n < 2) return;

      // ignore outside plot area
      if (x < pad || x > rect.width - pad || y < 0 || y > rect.height) {
        hide();
        return;
      }

      const t = (x - pad) / plotW;
      const idx = Math.max(0, Math.min(n - 1, Math.round(t * (n - 1))));

      const label = series.labels[idx] ?? "—";
      const f = series.flows[idx] ?? 0;
      const a = series.acl[idx] ?? 0;
      const d = series.ddos[idx] ?? 0;
      const al = series.allowed[idx] ?? 0;

      tooltip.innerHTML =
        `<div><b>${label}</b></div>` +
        `<div>flows/sec: <b>${f}</b></div>` +
        `<div>acl drops/sec: <b>${a}</b></div>` +
        `<div>ddos flags/sec: <b>${d}</b></div>` +
        `<div>allowed/sec: <b>${al}</b></div>`;

      // position inside chartWrap
      const wrapRect = canvas.parentElement.getBoundingClientRect();
      const left = (ev.clientX - wrapRect.left) + 14;
      const top = (ev.clientY - wrapRect.top) + 14;

      tooltip.style.left = `${left}px`;
      tooltip.style.top = `${top}px`;
      tooltip.style.display = "block";
    }

    canvas.addEventListener("mousemove", onMove);
    canvas.addEventListener("mouseleave", hide);
  }

  // ---- Events table ----
  function renderEvents(list) {
    if (!eventsBody) return;
    const arr = Array.isArray(list) ? list : [];

    if (arr.length === 0) {
      eventsBody.innerHTML = `<tr><td colspan="4" style="color: rgba(255,255,255,.6)">Nema događaja.</td></tr>`;
      return;
    }

    eventsBody.innerHTML = arr.slice(0, 30).map((e) => {
      const ts = fmtIso(e.ts);
      const lvl = (e.level || "INFO").toUpperCase();
      const msg = e.msg || "";
      const extra = e.extra ? JSON.stringify(e.extra) : "";
      return `
        <tr>
          <td>${ts}</td>
          <td><code>${lvl}</code></td>
          <td>${msg}</td>
          <td><code>${extra}</code></td>
        </tr>
      `;
    }).join("");
  }

  function applyData(data) {
    if (!data) {
      setStatus("Status: nema podataka");
      return;
    }

    if (elUpdatedAt) elUpdatedAt.textContent = fmtIso(data.updated_at);
    setStatus("Status: OK (dohvat uspješan)");

    const c = data.counters || {};
    if (elKpiEvents) elKpiEvents.textContent = c.events_total ?? 0;
    if (elKpiAcl) elKpiAcl.textContent = c.acl_drops_total ?? 0;
    if (elKpiDdos) elKpiDdos.textContent = c.ddos_flags_total ?? 0;
    if (elKpiAllowed) elKpiAllowed.textContent = c.allowed_total ?? 0;

    const ts = data.timeseries || {};
    series.labels = (ts.labels || []).slice(-MAX_POINTS);
    series.flows = (ts.flows_per_sec || []).slice(-MAX_POINTS);
    series.acl = (ts.acl_drops_per_sec || []).slice(-MAX_POINTS);
    series.ddos = (ts.ddos_flags_per_sec || []).slice(-MAX_POINTS);
    series.allowed = (ts.allowed_per_sec || []).slice(-MAX_POINTS);
    clampToMax();

    drawChart();
    renderEvents(data.last_events);
  }

  async function tick() {
    try {
      const data = await fetchJsonSafe(API_URL);
      applyData(data);
    } catch (e) {
      console.error(e);
      setStatus("Status: API error (pogledaj Console)");
    }
  }

  // init
  bindTooltip();
  tick();
  setInterval(tick, 1000);

  // redraw on resize
  window.addEventListener("resize", () => drawChart());
})();
