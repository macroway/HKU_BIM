/**
 * CheckBIM Agent — Loop2: plan view + agent timeline
 */

const TYPE_COLORS = {
  IfcWall: { fill: 'rgba(91, 143, 212, 0.35)', stroke: '#5b8fd4' },
  IfcBeam: { fill: 'rgba(155, 180, 120, 0.35)', stroke: '#9bb478' },
  IfcPipeSegment: { fill: 'rgba(212, 165, 116, 0.35)', stroke: '#d4a574' },
  IfcDoor: { fill: 'rgba(180, 140, 200, 0.35)', stroke: '#b48cc8' },
};

const TOOL_LABELS = {
  run_collision_check: '几何碰撞检测',
  run_attribute_check: '属性完整性检查',
  get_model_info: '读取模型概况',
};

const PLANNER_LABELS = {
  rules: '规则路由',
  llm: 'LLM',
  doubao: 'Doubao',
};

async function loadLlmStatus() {
  try {
    const res = await fetch('/api/llm/status');
    if (!res.ok) return;
    const s = await res.json();
    const badge = el('llm-badge');
    if (!badge) return;
    if (s.available && s.provider === 'ark') {
      badge.textContent = `Doubao · ${s.model || ''}`;
    } else if (s.available) {
      badge.textContent = `LLM · ${s.model || ''}`;
    } else {
      badge.textContent = '离线 · rules';
    }
    el('planner-tag').textContent = s.available
      ? `规划器 · ${PLANNER_LABELS[s.planner_label] || s.planner_label} · 待命`
      : '规划器 · 规则路由 · 待命';
  } catch (_) { /* ignore */ }
}

const QUICK_CHIPS = [
  { label: '交付前过一遍', message: '交付前帮我过一遍' },
  { label: '有没有硬碰', message: '有没有硬碰' },
  { label: '防火等级齐全吗', message: '防火等级齐全吗' },
  { label: '统计构件', message: '统计一下模型情况' },
  { label: '查碰撞', message: '帮我查碰撞' },
  { label: '查属性', message: '查属性完整性' },
];

let currentModelId = null;
let previewElements = [];
let collisionPairs = [];
let highlightPair = null;
let canvasCtx = null;
let viewTransform = null;

const el = (id) => document.getElementById(id);

function setError(msg) {
  el('entry-error').textContent = msg || '';
}

function enableAgent(enabled) {
  el('chat-input').disabled = !enabled;
  el('btn-send').disabled = !enabled;
  document.querySelectorAll('.chip').forEach((c) => { c.disabled = !enabled; });
}

function typeColor(type) {
  return TYPE_COLORS[type] || { fill: 'rgba(140, 140, 140, 0.3)', stroke: '#888' };
}

function initCanvas() {
  const canvas = el('plan-canvas');
  const box = canvas.parentElement;
  const dpr = window.devicePixelRatio || 1;
  const w = box.clientWidth;
  const h = Math.max(box.clientHeight, 320);
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';
  canvasCtx = canvas.getContext('2d');
  canvasCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
  drawPlanView();
}

function computeTransform(elements) {
  if (!elements.length) return null;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const e of elements) {
    const { min, max } = e.aabb;
    minX = Math.min(minX, min[0]);
    minY = Math.min(minY, min[1]);
    maxX = Math.max(maxX, max[0]);
    maxY = Math.max(maxY, max[1]);
  }
  const pad = Math.max((maxX - minX), (maxY - minY)) * 0.08 + 0.5;
  return { minX: minX - pad, minY: minY - pad, maxX: maxX + pad, maxY: maxY + pad };
}

function worldToCanvas(x, y, bounds, cw, ch) {
  const rangeX = bounds.maxX - bounds.minX || 1;
  const rangeY = bounds.maxY - bounds.minY || 1;
  const scale = Math.min((cw - 40) / rangeX, (ch - 40) / rangeY);
  const ox = 20 + (cw - 40 - rangeX * scale) / 2;
  const oy = 20 + (ch - 40 - rangeY * scale) / 2;
  return {
    x: ox + (x - bounds.minX) * scale,
    y: ch - (oy + (y - bounds.minY) * scale),
    scale,
  };
}

function drawPlanView() {
  const canvas = el('plan-canvas');
  if (!canvasCtx) return;
  const cw = parseInt(canvas.style.width, 10);
  const ch = parseInt(canvas.style.height, 10);
  canvasCtx.clearRect(0, 0, cw, ch);

  el('canvas-empty').hidden = previewElements.length > 0;

  if (!previewElements.length) return;

  const bounds = computeTransform(previewElements);
  viewTransform = { bounds, cw, ch };

  canvasCtx.strokeStyle = '#2a3038';
  canvasCtx.lineWidth = 1;
  canvasCtx.strokeRect(20, 20, cw - 40, ch - 40);

  canvasCtx.fillStyle = '#4a5259';
  canvasCtx.font = '10px sans-serif';
  canvasCtx.fillText('平面俯视图 (X–Y)', 24, ch - 8);

  const hitIds = new Set();
  if (highlightPair) {
    hitIds.add(highlightPair.a);
    hitIds.add(highlightPair.b);
  } else if (collisionPairs.length) {
    collisionPairs.forEach((p) => { hitIds.add(p.a); hitIds.add(p.b); });
  }

  for (const e of previewElements) {
    const { min, max } = e.aabb;
    const p1 = worldToCanvas(min[0], min[1], bounds, cw, ch);
    const p2 = worldToCanvas(max[0], max[1], bounds, cw, ch);
    const x = Math.min(p1.x, p2.x);
    const y = Math.min(p1.y, p2.y);
    const w = Math.abs(p2.x - p1.x);
    const h = Math.abs(p2.y - p1.y);

    const isHit = hitIds.has(e.id);
    const colors = typeColor(e.type);
    canvasCtx.fillStyle = isHit ? 'rgba(224, 108, 108, 0.45)' : colors.fill;
    canvasCtx.strokeStyle = isHit ? '#e06c6c' : colors.stroke;
    canvasCtx.lineWidth = isHit ? 2 : 1;
    canvasCtx.fillRect(x, y, Math.max(w, 2), Math.max(h, 2));
    canvasCtx.strokeRect(x, y, Math.max(w, 2), Math.max(h, 2));

    if (isHit && e.name) {
      canvasCtx.fillStyle = '#eef1f4';
      canvasCtx.font = '10px sans-serif';
      canvasCtx.fillText(e.name || e.id, x + 2, y - 3);
    }
  }
}

function appendBubble(role, text, extraHtml) {
  const log = el('chat-log');
  const div = document.createElement('div');
  div.className = 'bubble ' + role;
  const who = role === 'user' ? '你' : 'CheckBIM Agent';
  div.innerHTML = `<div class="who">${who}</div><div class="body">${text}${extraHtml || ''}</div>`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}

function removeTyping() {
  el('chat-log').querySelectorAll('.bubble.typing').forEach((n) => n.remove());
}

function setTimeline(steps) {
  const container = el('timeline-steps');
  container.innerHTML = '';
  if (!steps.length) {
    container.innerHTML = '<div class="t-step"><span class="dot"></span><span>等待指令…</span></div>';
    return;
  }
  steps.forEach((s) => {
    const div = document.createElement('div');
    div.className = 't-step ' + (s.state || '');
    div.innerHTML = `<span class="dot"></span><span>${s.text}</span>`;
    container.appendChild(div);
  });
}

async function animateTimeline(toolTraces, didRun) {
  if (!didRun) {
    setTimeline([{ text: '解析意图', state: 'done' }, { text: '需要更明确的检查指令', state: 'done' }]);
    return;
  }
  setTimeline([{ text: '解析意图', state: 'active' }]);
  await sleep(350);
  setTimeline([{ text: '解析意图', state: 'done' }]);
  for (let i = 0; i < toolTraces.length; i++) {
    const t = toolTraces[i];
    const label = TOOL_LABELS[t.tool] || t.tool;
    const steps = [{ text: '解析意图', state: 'done' }];
    for (let j = 0; j < i; j++) {
      steps.push({ text: '执行 · ' + (TOOL_LABELS[toolTraces[j].tool] || toolTraces[j].tool), state: 'done' });
    }
    steps.push({ text: '执行 · ' + label, state: 'active' });
    setTimeline(steps);
    await sleep(400);
  }
  const done = [{ text: '解析意图', state: 'done' }];
  toolTraces.forEach((t) => {
    done.push({ text: '执行 · ' + (TOOL_LABELS[t.tool] || t.tool), state: 'done' });
  });
  done.push({ text: '生成检查摘要', state: 'done' });
  setTimeline(done);
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function renderCollisionCards(pairs) {
  collisionPairs = pairs || [];
  const list = el('collision-list');
  if (!pairs || !pairs.length) {
    list.innerHTML = '<div class="empty-hint">暂无冲突</div>';
    el('stat-collisions').textContent = '0';
    el('stat-collisions').className = 'num ok';
    drawPlanView();
    return;
  }
  el('stat-collisions').textContent = String(pairs.length);
  el('stat-collisions').className = 'num danger';
  list.innerHTML = '';
  pairs.forEach((p, idx) => {
    const card = document.createElement('div');
    card.className = 'collision-card';
    card.innerHTML = `
      <div class="pair"><span>#${idx + 1}</span> ${p.a_name || p.a} ↔ ${p.b_name || p.b}</div>
      <div class="types">${p.a_type} × ${p.b_type}</div>`;
    card.onclick = () => {
      document.querySelectorAll('.collision-card').forEach((c) => c.classList.remove('active'));
      card.classList.add('active');
      highlightPair = p;
      drawPlanView();
    };
    list.appendChild(card);
  });
  if (pairs.length) {
    highlightPair = pairs[0];
    list.firstChild?.classList.add('active');
  }
  drawPlanView();
}

function renderAttrCards(missing) {
  const list = el('attr-list');
  if (!missing || !missing.length) {
    list.innerHTML = '<div class="empty-hint">属性完整 ✓</div>';
    el('stat-attrs').textContent = '0';
    el('stat-attrs').className = 'num ok';
    return;
  }
  el('stat-attrs').textContent = String(missing.length);
  el('stat-attrs').className = 'num danger';
  list.innerHTML = '';
  missing.forEach((m) => {
    const card = document.createElement('div');
    card.className = 'attr-card';
    card.innerHTML = `<span class="field">${m.field}</span><strong>${m.id}</strong> <span style="color:#8a9199">${m.type}</span>`;
    list.appendChild(card);
  });
}

async function loadPreview(modelId) {
  const res = await fetch('/api/models/' + encodeURIComponent(modelId) + '/preview');
  if (!res.ok) return;
  const data = await res.json();
  previewElements = data.elements || [];
  el('stat-elements').textContent = String(data.element_count);
  collisionPairs = [];
  highlightPair = null;
  renderCollisionCards([]);
  renderAttrCards([]);
  initCanvas();
}

async function loadSamples() {
  const res = await fetch('/api/models/samples');
  const samples = await res.json();
  const list = el('sample-list');
  list.innerHTML = '';
  samples.forEach((s) => {
    const li = document.createElement('li');
    li.innerHTML = `<span>${s.name}</span>`;
    const btn = document.createElement('button');
    btn.textContent = '载入';
    btn.onclick = () => selectSample(s.id);
    li.appendChild(btn);
    list.appendChild(li);
  });
}

function renderChips() {
  const box = el('chips');
  box.innerHTML = '';
  QUICK_CHIPS.forEach((c) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'chip';
    btn.textContent = c.label;
    btn.disabled = true;
    btn.onclick = () => sendChat(c.message);
    box.appendChild(btn);
  });
}

async function onModelLoaded(modelId, label) {
  currentModelId = modelId;
  el('model-badge').textContent = label;
  enableAgent(true);
  setError('');
  await loadPreview(modelId);
  setTimeline([]);
  appendBubble('agent', '模型已就绪。你可以直接点下方快捷指令，或用自然语言说明检查意图。');
}

async function selectSample(sampleId) {
  setError('');
  const res = await fetch('/api/models/select/' + sampleId, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    setError(typeof err.detail === 'string' ? err.detail : '载入样例失败');
    return;
  }
  const data = await res.json();
  el('chat-log').innerHTML = '';
  await onModelLoaded(data.model_id, sampleId);
}

async function uploadFile(file) {
  setError('');
  const form = new FormData();
  form.append('file', file);
  const res = await fetch('/api/models/upload', { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    setError(err.detail || '上传失败');
    return;
  }
  const data = await res.json();
  el('chat-log').innerHTML = '';
  await onModelLoaded(data.model_id, file.name);
}

async function sendChat(presetMessage) {
  const input = el('chat-input');
  const message = (typeof presetMessage === 'string' ? presetMessage : input.value.trim());
  if (!message || !currentModelId) return;
  input.value = '';
  appendBubble('user', message);
  enableAgent(false);
  appendBubble('agent', '正在规划并调用检查工具…', '');
  el('chat-log').lastElementChild?.classList.add('typing');
  setTimeline([{ text: '解析意图', state: 'active' }]);

  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_id: currentModelId, message }),
  });

  removeTyping();
  enableAgent(true);

  if (!res.ok) {
    appendBubble('agent', '请求失败，请重试。');
    setTimeline([]);
    return;
  }

  const data = await res.json();
  let toolTags = '';
  if (data.did_run_tools) {
    toolTags = data.tool_traces.map((t) =>
      `<span class="tool-tag">${TOOL_LABELS[t.tool] || t.tool}</span>`
    ).join('');
  }
  appendBubble('agent', data.reply, toolTags);

  await animateTimeline(data.tool_traces, data.did_run_tools);

  el('planner-tag').textContent = data.did_run_tools
    ? `规划器 · ${PLANNER_LABELS[data.planner] || data.planner} · 已调用 ${data.tool_traces.length} 个工具`
    : `规划器 · ${PLANNER_LABELS[data.planner] || data.planner} · 未执行工具`;

  if (data.results?.collision) {
    renderCollisionCards(data.results.collision.pairs);
  }
  if (data.results?.attributes) {
    renderAttrCards(data.results.attributes.missing);
  }
}

function bindEvents() {
  el('btn-upload').onclick = () => el('file-input').click();
  el('file-input').onchange = (e) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
  };

  const dropZone = el('drop-zone');
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files?.[0];
    if (file) uploadFile(file);
  });
  dropZone.onclick = () => el('file-input').click();

  el('btn-send').onclick = () => sendChat();
  el('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendChat();
  });

  window.addEventListener('resize', () => {
    if (previewElements.length) initCanvas();
  });
}

renderChips();
bindEvents();
loadSamples();
loadLlmStatus();
setTimeline([]);
