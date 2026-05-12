from flask import Flask, request, jsonify, render_template_string
import time

app = Flask(__name__)

# ─────────────────────────────────────────────
#  In-memory user database (UID → user data)
# ─────────────────────────────────────────────
USERS = {
    "04A3F91B": {"name": "Khushi Verma",   "balance": 500.0},
    "1B2C3D4E": {"name": "Khan Hanzala",  "balance": 320.0},
    "DEADBEEF": {"name": "Ansari Fauzan",  "balance": 150.0},
}

# Track currently scanned user
current_uid = {"value": None}

# ─────────────────────────────────────────────
#  HTML / CSS / JS  (render_template_string)
# ─────────────────────────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>VoltoCharge — Smart EV Station</title>

<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">

<style>
/* ══════════════════════════════════════
   CSS VARIABLES & RESET
══════════════════════════════════════ */
:root {
  --bg:        #050d1a;
  --panel:     #0b1628;
  --border:    #0e2a4a;
  --accent:    #00e5ff;
  --accent2:   #7c3aed;
  --accent3:   #22d3ee;
  --green:     #10b981;
  --red:       #ef4444;
  --yellow:    #f59e0b;
  --text:      #e0f2fe;
  --muted:     #4a7fa5;
  --card-bg:   linear-gradient(135deg, #1a3a5c 0%, #0f2540 50%, #1a1040 100%);
  --glow:      0 0 30px rgba(0,229,255,0.25);
  --glow2:     0 0 60px rgba(0,229,255,0.12);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

/* ── Animated grid background ── */
body::before {
  content: '';
  position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(0,229,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,229,255,0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
  z-index: 0;
}

body::after {
  content: '';
  position: fixed; inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(0,80,120,0.35) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* ══════════════════════════════════════
   LAYOUT
══════════════════════════════════════ */
.app {
  position: relative; z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px 60px;
}

/* ── Header ── */
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0 32px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 40px;
}

.logo {
  display: flex; align-items: center; gap: 14px;
}

.logo-icon {
  width: 52px; height: 52px;
  background: linear-gradient(135deg, var(--accent2), var(--accent));
  border-radius: 14px;
  display: grid; place-items: center;
  font-size: 26px;
  box-shadow: var(--glow);
}

.logo-text {
  font-family: 'Orbitron', monospace;
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-sub {
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 3px;
  text-transform: uppercase;
}

.station-id {
  text-align: right;
}

.station-id p {
  font-family: 'Orbitron', monospace;
  font-size: 0.75rem;
  color: var(--muted);
  letter-spacing: 2px;
}

.station-id .id-val {
  font-size: 1rem;
  color: var(--accent);
  font-weight: 600;
}

/* ── Status bar ── */
#statusBar {
  background: var(--panel);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: 10px;
  padding: 14px 20px;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
  transition: all 0.4s ease;
  min-height: 54px;
}

#statusBar .sb-icon { font-size: 1.3rem; flex-shrink: 0; }
#statusBar .sb-text { flex: 1; }
#statusBar .sb-user {
  font-family: 'Orbitron', monospace;
  font-size: 0.75rem;
  color: var(--muted);
  text-align: right;
}

#statusBar.ok   { border-left-color: var(--green);  }
#statusBar.err  { border-left-color: var(--red);    }
#statusBar.warn { border-left-color: var(--yellow); }
#statusBar.info { border-left-color: var(--accent); }

/* ── Main grid ── */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 600px) {
  .grid { grid-template-columns: 1fr; }
}

/* ── Panel card ── */
.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.3s;
}

.panel::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.panel:hover { box-shadow: var(--glow2); }

.panel-title {
  font-family: 'Orbitron', monospace;
  font-size: 0.7rem;
  letter-spacing: 3px;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-title span { font-size: 1rem; }

/* ══════════════════════════════════════
   RFID PANEL  (spans 2 cols)
══════════════════════════════════════ */
.rfid-panel {
  grid-column: span 2;
}

.rfid-arena {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 20px;
  flex-wrap: wrap;
  min-height: 200px;
}

/* ── RFID Card ── */
.rfid-card-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.rfid-card {
  width: 190px;
  height: 120px;
  background: var(--card-bg);
  border: 1px solid rgba(0,229,255,0.3);
  border-radius: 14px;
  padding: 16px;
  cursor: grab;
  position: relative;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  user-select: none;
  touch-action: none;
}

.rfid-card:active { cursor: grabbing; transform: scale(1.05) rotate(2deg); }

.rfid-card .chip {
  width: 36px; height: 28px;
  background: linear-gradient(135deg, #d4af37, #f5d06a, #b8960c);
  border-radius: 5px;
  margin-bottom: 10px;
  position: relative;
  overflow: hidden;
}
.rfid-card .chip::before {
  content: '';
  position: absolute; inset: 3px;
  border: 1px solid rgba(0,0,0,0.25);
  border-radius: 3px;
}

.rfid-card .card-uid {
  font-family: 'Orbitron', monospace;
  font-size: 0.65rem;
  color: rgba(0,229,255,0.7);
  letter-spacing: 2px;
}

.rfid-card .card-brand {
  position: absolute;
  bottom: 12px; right: 14px;
  font-family: 'Orbitron', monospace;
  font-size: 0.6rem;
  color: rgba(255,255,255,0.4);
  letter-spacing: 1px;
}

.rfid-card .waves {
  position: absolute;
  top: 12px; right: 12px;
  color: rgba(0,229,255,0.5);
  font-size: 1.1rem;
}

.card-label {
  font-size: 0.75rem;
  color: var(--muted);
  text-align: center;
}

/* ── Scan arrow ── */
.scan-arrow {
  font-size: 2rem;
  color: var(--accent);
  animation: pulse-arrow 1.5s infinite;
  flex-shrink: 0;
}

@keyframes pulse-arrow {
  0%, 100% { opacity: 0.3; transform: translateX(0); }
  50%       { opacity: 1;   transform: translateX(6px); }
}

/* ── Drop zone ── */
.drop-zone {
  width: 220px;
  height: 140px;
  border: 2px dashed var(--muted);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.25s ease;
  position: relative;
  background: rgba(0,229,255,0.02);
}

.drop-zone.drag-over {
  border-color: var(--accent);
  background: rgba(0,229,255,0.08);
  box-shadow: 0 0 40px rgba(0,229,255,0.3);
  transform: scale(1.04);
}

.drop-zone.scanned {
  border-color: var(--green);
  background: rgba(16,185,129,0.08);
  box-shadow: 0 0 40px rgba(16,185,129,0.3);
  animation: scan-flash 0.6s ease;
}

@keyframes scan-flash {
  0%   { background: rgba(16,185,129,0.35); }
  100% { background: rgba(16,185,129,0.08); }
}

.drop-zone-icon { font-size: 2.5rem; }
.drop-zone-text {
  font-family: 'Orbitron', monospace;
  font-size: 0.65rem;
  letter-spacing: 2px;
  color: var(--muted);
  text-align: center;
}

/* Scan ring animation */
.ring-wrap {
  position: absolute; inset: -12px;
  pointer-events: none;
}

.ring {
  position: absolute; inset: 0;
  border-radius: 20px;
  border: 2px solid var(--accent);
  opacity: 0;
  animation: ring-pulse 2s infinite;
}

.ring:nth-child(2) { animation-delay: 0.7s; }

@keyframes ring-pulse {
  0%   { opacity: 0.6; transform: scale(1); }
  100% { opacity: 0;   transform: scale(1.2); }
}

/* ══════════════════════════════════════
   USER INFO PANEL
══════════════════════════════════════ */
.user-panel { grid-column: span 1; }

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.88rem;
}

.info-row:last-child { border-bottom: none; }

.info-label {
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.info-value {
  font-family: 'Orbitron', monospace;
  font-size: 0.85rem;
  color: var(--text);
}

.balance-big {
  font-family: 'Orbitron', monospace;
  font-size: 1.9rem;
  font-weight: 900;
  color: var(--accent);
  text-shadow: 0 0 20px rgba(0,229,255,0.5);
  margin: 10px 0 4px;
  line-height: 1;
}

.balance-label {
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.uid-badge {
  display: inline-block;
  background: rgba(0,229,255,0.08);
  border: 1px solid rgba(0,229,255,0.2);
  border-radius: 6px;
  padding: 3px 10px;
  font-family: 'Orbitron', monospace;
  font-size: 0.72rem;
  color: var(--accent3);
  letter-spacing: 1px;
}

/* ══════════════════════════════════════
   CHARGING + RECHARGE PANELS
══════════════════════════════════════ */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

label.field-label {
  font-size: 0.75rem;
  color: var(--muted);
  letter-spacing: 2px;
  text-transform: uppercase;
}

input[type="number"] {
  background: rgba(0,229,255,0.04);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 16px;
  color: var(--text);
  font-family: 'Orbitron', monospace;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
}

input[type="number"]:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(0,229,255,0.1);
}

input[type="number"]::placeholder { color: var(--muted); font-size: 0.85rem; }

/* Remove number arrows */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button { -webkit-appearance: none; }

/* ── Buttons ── */
.btn {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 10px;
  font-family: 'Orbitron', monospace;
  font-size: 0.75rem;
  letter-spacing: 2px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
}

.btn::after {
  content: '';
  position: absolute; inset: 0;
  background: white;
  opacity: 0;
  transition: opacity 0.2s;
}

.btn:hover::after { opacity: 0.06; }
.btn:active { transform: scale(0.98); }
.btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

.btn-charge {
  background: linear-gradient(135deg, #0e7490, #06b6d4);
  color: #fff;
  box-shadow: 0 4px 20px rgba(6,182,212,0.3);
}

.btn-recharge {
  background: linear-gradient(135deg, #5b21b6, #7c3aed);
  color: #fff;
  box-shadow: 0 4px 20px rgba(124,58,237,0.3);
}

.btn:hover:not(:disabled) { filter: brightness(1.15); transform: translateY(-1px); }

/* ── Cost hint ── */
.cost-hint {
  font-size: 0.75rem;
  color: var(--muted);
  text-align: center;
  margin-top: 6px;
}

/* ── Progress bar ── */
.progress-wrap {
  height: 4px;
  background: var(--border);
  border-radius: 4px;
  margin-top: 12px;
  overflow: hidden;
  display: none;
}

.progress-bar {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--accent2), var(--accent));
  border-radius: 4px;
  transition: width 0.9s linear;
}

/* ══════════════════════════════════════
   HISTORY LOG
══════════════════════════════════════ */
.log-panel { grid-column: span 3; }

@media (max-width: 900px) { .log-panel { grid-column: span 2; } }
@media (max-width: 600px) { .log-panel { grid-column: span 1; } }

.log-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 220px;
  overflow-y: auto;
  padding-right: 4px;
}

.log-list::-webkit-scrollbar { width: 4px; }
.log-list::-webkit-scrollbar-track { background: transparent; }
.log-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.log-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(0,229,255,0.03);
  border-radius: 8px;
  border-left: 3px solid var(--border);
  font-size: 0.82rem;
  animation: log-in 0.3s ease;
}

@keyframes log-in {
  from { opacity: 0; transform: translateX(-10px); }
  to   { opacity: 1; transform: translateX(0); }
}

.log-item.log-ok   { border-left-color: var(--green); }
.log-item.log-err  { border-left-color: var(--red); }
.log-item.log-info { border-left-color: var(--accent); }
.log-item.log-warn { border-left-color: var(--yellow); }

.log-time {
  font-family: 'Orbitron', monospace;
  font-size: 0.68rem;
  color: var(--muted);
  flex-shrink: 0;
}

.log-msg { flex: 1; }

.log-empty {
  text-align: center;
  color: var(--muted);
  font-size: 0.82rem;
  padding: 20px;
}

/* ══════════════════════════════════════
   SCANNING ANIMATION OVERLAY
══════════════════════════════════════ */
.scan-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(4px);
  z-index: 999;
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.scan-overlay.active { display: flex; animation: fade-in 0.2s ease; }

@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }

.scan-spinner {
  width: 80px; height: 80px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.scan-overlay p {
  font-family: 'Orbitron', monospace;
  font-size: 0.8rem;
  letter-spacing: 3px;
  color: var(--accent);
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

/* ══════════════════════════════════════
   MISC
══════════════════════════════════════ */
.no-user-msg {
  text-align: center;
  color: var(--muted);
  font-size: 0.82rem;
  padding: 30px 0;
}

.no-user-icon { font-size: 2.5rem; margin-bottom: 8px; }

.available-cards {
  margin-top: 12px;
  border-top: 1px solid var(--border);
  padding-top: 12px;
}

.available-cards h4 {
  font-family: 'Orbitron', monospace;
  font-size: 0.6rem;
  letter-spacing: 2px;
  color: var(--muted);
  margin-bottom: 8px;
}

.card-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
  font-size: 0.78rem;
  color: var(--muted);
}

.card-chip .dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent);
}
</style>
</head>
<body>

<!-- Scan overlay -->
<div class="scan-overlay" id="scanOverlay">
  <div class="scan-spinner"></div>
  <p>SCANNING RFID...</p>
</div>

<div class="app">

  <!-- HEADER -->
  <header>
    <div class="logo">
      <div class="logo-icon">⚡</div>
      <div>
        <div class="logo-text">VoltoCharge</div>
        <div class="logo-sub">Smart EV Charging Station</div>
      </div>
    </div>
    <div class="station-id">
      <p>Station ID</p>
      <p class="id-val" style="font-family:'Orbitron',monospace;">VCST-MH-042</p>
      <p id="clockDisplay" style="color:var(--accent3);font-size:0.72rem;margin-top:4px;font-family:'Orbitron',monospace;"></p>
    </div>
  </header>

  <!-- STATUS BAR -->
  <div id="statusBar" class="info">
    <span class="sb-icon">ℹ️</span>
    <span class="sb-text">Tap &amp; drag your RFID card onto the reader to begin.</span>
    <span class="sb-user" id="sbUser"></span>
  </div>

  <div class="grid">

    <!-- ══ RFID PANEL ══ -->
    <div class="panel rfid-panel">
      <div class="panel-title"><span>📡</span> RFID Authentication</div>

      <div class="rfid-arena">
        <!-- Card -->
        <div class="rfid-card-wrap">
          <div class="rfid-card" id="rfidCard"
               draggable="true"
               ondragstart="onDragStart(event)"
               ondragend="onDragEnd(event)">
            <div class="chip"></div>
            <div class="card-uid">04A3F91B</div>
            <div class="waves">📶</div>
            <div class="card-brand">VOLTOCARD</div>
          </div>
          <div class="card-label">Drag card → Reader</div>

          <!-- More cards info -->
          <div class="available-cards">
            <h4>Available Demo Cards</h4>
            <div class="card-chip"><div class="dot"></div>04A3F91B — Khushi Verma</div>
            <div class="card-chip"><div class="dot" style="background:var(--accent2)"></div>1B2C3D4E — Khan Hanzala</div>
            <div class="card-chip"><div class="dot" style="background:var(--yellow)"></div>DEADBEEF — Ansari Fauzan</div>
          </div>
        </div>

        <!-- Arrow -->
        <div class="scan-arrow">→</div>

        <!-- Drop zone -->
        <div>
          <div class="drop-zone" id="dropZone"
               ondragover="onDragOver(event)"
               ondragleave="onDragLeave(event)"
               ondrop="onDrop(event)">
            <div class="ring-wrap">
              <div class="ring"></div>
              <div class="ring"></div>
            </div>
            <div class="drop-zone-icon">📲</div>
            <div class="drop-zone-text">RFID READER<br>DROP HERE</div>
          </div>

          <!-- UID switcher for demo -->
          <div style="margin-top:14px;text-align:center;">
            <label class="field-label" style="display:block;margin-bottom:6px;">Switch UID (Demo)</label>
            <select id="uidSelect" style="background:var(--panel);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:8px 12px;font-family:'DM Sans',sans-serif;font-size:0.85rem;outline:none;cursor:pointer;width:100%;">
              <option value="04A3F91B">04A3F91B — Khushi</option>
              <option value="1B2C3D4E">1B2C3D4E — Hanzala</option>
              <option value="DEADBEEF">DEADBEEF — Fauzan</option>
              <option value="INVALID00">INVALID00 — Unknown</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ USER INFO PANEL ══ -->
    <div class="panel user-panel" id="userPanel">
      <div class="panel-title"><span>👤</span> User Profile</div>
      <div id="userInfo">
        <div class="no-user-msg">
          <div class="no-user-icon">🔒</div>
          <div>Scan card to load profile</div>
        </div>
      </div>
    </div>

    <!-- ══ CHARGING PANEL ══ -->
    <div class="panel">
      <div class="panel-title"><span>⚡</span> Start Charging</div>

      <div class="form-group">
        <label class="field-label" for="chargeMin">Duration (minutes)</label>
        <input type="number" id="chargeMin" placeholder="e.g. 30" min="1" max="480" />
      </div>

      <div id="chargeCostPreview" class="cost-hint">₹5 per minute · Enter minutes above</div>

      <button class="btn btn-charge" id="chargeBtn" onclick="startCharging()" disabled>
        ⚡ Start Charging
      </button>

      <div class="progress-wrap" id="progressWrap">
        <div class="progress-bar" id="progressBar"></div>
      </div>
    </div>

    <!-- ══ RECHARGE PANEL ══ -->
    <div class="panel">
      <div class="panel-title"><span>💳</span> Recharge Wallet</div>

      <div class="form-group">
        <label class="field-label" for="rechargeAmt">Amount (₹)</label>
        <input type="number" id="rechargeAmt" placeholder="e.g. 500" min="1" max="10000" />
      </div>

      <div class="cost-hint" style="margin-bottom:16px;">Instant balance top-up</div>

      <button class="btn btn-recharge" id="rechargeBtn" onclick="doRecharge()" disabled>
        💳 Add Balance
      </button>
    </div>

    <!-- ══ LOG PANEL ══ -->
    <div class="panel log-panel">
      <div class="panel-title" style="justify-content:space-between;">
        <span><span>🗒️</span>&nbsp;&nbsp;Activity Log</span>
        <button onclick="clearLog()" style="background:none;border:1px solid var(--border);border-radius:6px;color:var(--muted);padding:3px 10px;font-size:0.7rem;cursor:pointer;font-family:'Orbitron',monospace;letter-spacing:1px;">CLEAR</button>
      </div>
      <ul class="log-list" id="logList">
        <li class="log-empty">No activity yet.</li>
      </ul>
    </div>

  </div><!-- /grid -->
</div><!-- /app -->

<script>
// ─────────────────────────────────────────────
//  STATE
// ─────────────────────────────────────────────
let currentUser = null;
let logEntries  = [];

// ─────────────────────────────────────────────
//  CLOCK
// ─────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('clockDisplay').textContent =
    now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

// ─────────────────────────────────────────────
//  DRAG & DROP
// ─────────────────────────────────────────────
function onDragStart(e) {
  e.dataTransfer.setData('text/plain', 'rfid-card');
  setTimeout(() => document.getElementById('rfidCard').style.opacity = '0.5', 0);
}

function onDragEnd(e) {
  document.getElementById('rfidCard').style.opacity = '1';
  document.getElementById('dropZone').classList.remove('drag-over');
}

function onDragOver(e) {
  e.preventDefault();
  document.getElementById('dropZone').classList.add('drag-over');
}

function onDragLeave(e) {
  document.getElementById('dropZone').classList.remove('drag-over');
}

function onDrop(e) {
  e.preventDefault();
  document.getElementById('dropZone').classList.remove('drag-over');
  if (e.dataTransfer.getData('text/plain') === 'rfid-card') {
    simulateScan();
  }
}

// Touch support for mobile
const card = document.getElementById('rfidCard');
const drop = document.getElementById('dropZone');
let touchDragging = false;
let ghost = null;

card.addEventListener('touchstart', (e) => {
  touchDragging = true;
  ghost = card.cloneNode(true);
  ghost.style.cssText = `position:fixed;opacity:0.75;pointer-events:none;z-index:9999;width:${card.offsetWidth}px;border-radius:14px;`;
  document.body.appendChild(ghost);
}, { passive: true });

card.addEventListener('touchmove', (e) => {
  if (!touchDragging) return;
  const t = e.touches[0];
  ghost.style.left = (t.clientX - card.offsetWidth / 2) + 'px';
  ghost.style.top  = (t.clientY - card.offsetHeight / 2) + 'px';
  const rect = drop.getBoundingClientRect();
  if (t.clientX >= rect.left && t.clientX <= rect.right &&
      t.clientY >= rect.top  && t.clientY <= rect.bottom) {
    drop.classList.add('drag-over');
  } else {
    drop.classList.remove('drag-over');
  }
}, { passive: true });

card.addEventListener('touchend', (e) => {
  if (!touchDragging) return;
  touchDragging = false;
  if (ghost) { ghost.remove(); ghost = null; }
  const t = e.changedTouches[0];
  const rect = drop.getBoundingClientRect();
  if (t.clientX >= rect.left && t.clientX <= rect.right &&
      t.clientY >= rect.top  && t.clientY <= rect.bottom) {
    simulateScan();
  }
  drop.classList.remove('drag-over');
});

// ─────────────────────────────────────────────
//  RFID SCAN
// ─────────────────────────────────────────────
async function simulateScan() {
  const uid = document.getElementById('uidSelect').value;

  // Show overlay
  document.getElementById('scanOverlay').classList.add('active');

  try {
    const res  = await fetch('/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid })
    });
    const data = await res.json();

    if (data.success) {
      currentUser = data.user;
      renderUserInfo(data.user);
      setStatus('ok', `✅ Welcome back, ${data.user.name}!`, data.user.name);
      addLog('ok', `RFID scanned — ${data.user.name} | UID: ${uid} | Balance: ₹${data.user.balance}`);
      document.getElementById('dropZone').classList.add('scanned');
      setTimeout(() => document.getElementById('dropZone').classList.remove('scanned'), 1500);
      enableActions(true);
    } else {
      currentUser = null;
      renderUserInfo(null);
      setStatus('err', `❌ Invalid RFID: ${uid} — card not recognized.`);
      addLog('err', `Failed scan — UID: ${uid} — not in database`);
      enableActions(false);
    }
  } catch (err) {
    setStatus('err', '⚠️ Server error during scan.');
  } finally {
    document.getElementById('scanOverlay').classList.remove('active');
  }
}

// ─────────────────────────────────────────────
//  RENDER USER INFO
// ─────────────────────────────────────────────
function renderUserInfo(user) {
  const el = document.getElementById('userInfo');
  if (!user) {
    el.innerHTML = `<div class="no-user-msg">
      <div class="no-user-icon">🔒</div>
      <div>Scan card to load profile</div>
    </div>`;
    document.getElementById('sbUser').textContent = '';
    return;
  }
  el.innerHTML = `
    <div style="margin-bottom:18px;">
      <div style="font-size:1.1rem;font-weight:500;margin-bottom:4px;">${user.name}</div>
      <span class="uid-badge">${user.uid}</span>
    </div>
    <div class="balance-big">₹${parseFloat(user.balance).toFixed(2)}</div>
    <div class="balance-label">Available Balance</div>
    <div style="margin-top:18px;">
      <div class="info-row">
        <span class="info-label">Status</span>
        <span class="info-value" style="color:var(--green);">● Active</span>
      </div>
      <div class="info-row">
        <span class="info-label">Rate</span>
        <span class="info-value">₹5 / min</span>
      </div>
    </div>`;
  document.getElementById('sbUser').textContent = `Logged in as ${user.name}`;
}

// ─────────────────────────────────────────────
//  CHARGING
// ─────────────────────────────────────────────
document.getElementById('chargeMin').addEventListener('input', function() {
  const min = parseInt(this.value) || 0;
  const cost = min * 5;
  const el = document.getElementById('chargeCostPreview');
  if (min > 0) {
    el.innerHTML = `Estimated cost: <strong style="color:var(--accent)">₹${cost}</strong>`;
  } else {
    el.textContent = '₹5 per minute · Enter minutes above';
  }
});

async function startCharging() {
  if (!currentUser) return;
  const minutes = parseInt(document.getElementById('chargeMin').value);
  if (!minutes || minutes < 1) {
    setStatus('warn', '⚠️ Please enter a valid number of minutes.');
    return;
  }

  const btn = document.getElementById('chargeBtn');
  btn.disabled = true;
  btn.textContent = '⏳ Charging...';

  // Progress bar animation
  const wrap = document.getElementById('progressWrap');
  const bar  = document.getElementById('progressBar');
  wrap.style.display = 'block';
  bar.style.width = '0%';
  requestAnimationFrame(() => { bar.style.width = '100%'; });

  try {
    const res  = await fetch('/charge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid: currentUser.uid, minutes })
    });
    const data = await res.json();

    if (data.success) {
      currentUser = data.user;
      renderUserInfo(data.user);
      setStatus('ok', `⚡ Charged ${minutes} min — ₹${data.cost} deducted. New balance: ₹${data.user.balance}`);
      addLog('ok', `Charging ${minutes} min | Cost ₹${data.cost} | Balance ₹${data.user.balance}`);
      document.getElementById('chargeMin').value = '';
      document.getElementById('chargeCostPreview').textContent = '₹5 per minute · Enter minutes above';
    } else {
      setStatus('err', `❌ ${data.error}`);
      addLog('err', data.error);
    }
  } catch (err) {
    setStatus('err', '⚠️ Server error during charging.');
  } finally {
    setTimeout(() => {
      btn.disabled = false;
      btn.textContent = '⚡ Start Charging';
      wrap.style.display = 'none';
      bar.style.width = '0%';
    }, 1100);
  }
}

// ─────────────────────────────────────────────
//  RECHARGE
// ─────────────────────────────────────────────
async function doRecharge() {
  if (!currentUser) return;
  const amount = parseFloat(document.getElementById('rechargeAmt').value);
  if (!amount || amount < 1) {
    setStatus('warn', '⚠️ Enter a valid recharge amount.');
    return;
  }

  try {
    const res  = await fetch('/recharge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid: currentUser.uid, amount })
    });
    const data = await res.json();

    if (data.success) {
      currentUser = data.user;
      renderUserInfo(data.user);
      setStatus('ok', `💳 ₹${amount} added! New balance: ₹${data.user.balance}`);
      addLog('info', `Recharge ₹${amount} | Balance ₹${data.user.balance}`);
      document.getElementById('rechargeAmt').value = '';
    } else {
      setStatus('err', `❌ ${data.error}`);
    }
  } catch (err) {
    setStatus('err', '⚠️ Server error during recharge.');
  }
}

// ─────────────────────────────────────────────
//  HELPERS
// ─────────────────────────────────────────────
function enableActions(on) {
  document.getElementById('chargeBtn').disabled   = !on;
  document.getElementById('rechargeBtn').disabled = !on;
}

function setStatus(type, msg, user = '') {
  const icons = { ok: '✅', err: '❌', warn: '⚠️', info: 'ℹ️' };
  const bar = document.getElementById('statusBar');
  bar.className = type;
  bar.querySelector('.sb-icon').textContent = icons[type] || 'ℹ️';
  bar.querySelector('.sb-text').textContent = msg;
}

function addLog(type, msg) {
  const ul = document.getElementById('logList');
  // Remove empty placeholder
  const empty = ul.querySelector('.log-empty');
  if (empty) empty.remove();

  const now = new Date();
  const time = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  const li = document.createElement('li');
  li.className = `log-item log-${type}`;
  li.innerHTML = `<span class="log-time">${time}</span><span class="log-msg">${msg}</span>`;
  ul.insertBefore(li, ul.firstChild);

  // Cap at 20 entries
  while (ul.children.length > 20) ul.removeChild(ul.lastChild);
}

function clearLog() {
  document.getElementById('logList').innerHTML = '<li class="log-empty">No activity yet.</li>';
}
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/scan", methods=["POST"])
def scan():
    """Simulate RFID scan."""
    data = request.get_json()
    uid  = data.get("uid", "").strip().upper()

    time.sleep(1)  # Simulate scan delay

    if uid in USERS:
        user = USERS[uid]
        return jsonify({
            "success": True,
            "user": {
                "uid":     uid,
                "name":    user["name"],
                "balance": round(user["balance"], 2),
            }
        })
    else:
        return jsonify({"success": False, "error": f"UID {uid} not registered."})


@app.route("/charge", methods=["POST"])
def charge():
    """Deduct charging cost from balance."""
    data    = request.get_json()
    uid     = data.get("uid", "").strip().upper()
    minutes = int(data.get("minutes", 0))

    if uid not in USERS:
        return jsonify({"success": False, "error": "User not found. Please scan again."})

    if minutes < 1:
        return jsonify({"success": False, "error": "Invalid duration."})

    cost = minutes * 5.0   # ₹5 per minute

    if USERS[uid]["balance"] < cost:
        return jsonify({
            "success": False,
            "error": f"Insufficient balance. Need ₹{cost:.2f}, have ₹{USERS[uid]['balance']:.2f}."
        })

    time.sleep(1)  # Simulate charging delay

    USERS[uid]["balance"] -= cost
    USERS[uid]["balance"]  = round(USERS[uid]["balance"], 2)

    return jsonify({
        "success": True,
        "cost":    cost,
        "user": {
            "uid":     uid,
            "name":    USERS[uid]["name"],
            "balance": USERS[uid]["balance"],
        }
    })


@app.route("/recharge", methods=["POST"])
def recharge():
    """Add balance to user wallet."""
    data   = request.get_json()
    uid    = data.get("uid", "").strip().upper()
    amount = float(data.get("amount", 0))

    if uid not in USERS:
        return jsonify({"success": False, "error": "User not found."})

    if amount <= 0:
        return jsonify({"success": False, "error": "Invalid amount."})

    USERS[uid]["balance"] += amount
    USERS[uid]["balance"]  = round(USERS[uid]["balance"], 2)

    return jsonify({
        "success": True,
        "user": {
            "uid":     uid,
            "name":    USERS[uid]["name"],
            "balance": USERS[uid]["balance"],
        }
    })


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  VoltoCharge — Smart EV Charging Station")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True)