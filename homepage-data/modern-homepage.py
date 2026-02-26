import sys
import threading
import time

import docker
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
_client = None


def _docker_client():
    global _client
    if _client is None:
        _client = docker.from_env()
    return _client


def _service_url(service_name: str, ports: list[str]):
    port_mapping = {
        "vscode": "8080",
        "windowsserver": "8006",
        "windowsserver2022": "8006",
        "debian": "8007",
    }

    mapped = port_mapping.get(service_name)
    if mapped and mapped in ports:
        return f"http://localhost:{mapped}"
    if ports:
        return f"http://localhost:{ports[0]}"
    return None


def _compose_containers():
    dc = _docker_client()
    containers = dc.containers.list(all=True)
    managed = []
    for c in containers:
        labels = c.labels or {}
        if "com.docker.compose.project" not in labels:
            continue
        service = labels.get("com.docker.compose.service", "")
        if service == "modern-homepage":
            continue
        managed.append(c)
    return managed


def _display_name(service_name: str):
    display_names = {
        "vscode": "VS Code",
        "windowsserver": "Windows Server",
        "windowsserver2022": "Windows Server",
        "debian": "Debian Server",
    }
    return display_names.get(service_name, service_name)


def _icon(service_name: str):
    icons = {
        "vscode": "💻",
        "windowsserver": "🖥️",
        "windowsserver2022": "🖥️",
        "debian": "🐧",
    }
    return icons.get(service_name, "📦")


def _services():
    services = []
    for c in _compose_containers():
        labels = c.labels or {}
        service_name = labels.get("com.docker.compose.service", c.name)

        ports = []
        if c.ports:
            for _, host_bindings in c.ports.items():
                if not host_bindings:
                    continue
                for binding in host_bindings:
                    ports.append(str(binding.get("HostPort")))

        services.append(
            {
                "name": service_name,
                "display_name": _display_name(service_name),
                "container_name": c.name,
                "status": c.status,
                "image": (c.image.tags[0] if c.image.tags else "Unknown"),
                "ports": ports,
                "state": ("running" if c.status == "running" else "stopped"),
                "url": _service_url(service_name, ports),
                "icon": _icon(service_name),
            }
        )

    services.sort(key=lambda x: x["display_name"].lower())
    return services


def _container(name: str):
    return _docker_client().containers.get(name)


def _start(name: str):
    try:
        _container(name).start()
        return True, f"Service {name} gestartet"
    except Exception as e:
        return False, f"Fehler: {str(e)}"


def _stop(name: str):
    try:
        _container(name).stop(timeout=30)
        return True, f"Service {name} gestoppt"
    except Exception as e:
        return False, f"Fehler: {str(e)}"


def _restart(name: str):
    try:
        _container(name).restart(timeout=30)
        return True, f"Service {name} neugestartet"
    except Exception as e:
        return False, f"Fehler: {str(e)}"


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"de\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Theodor-Litt-Schule · Docker Dienste</title>
  <style>
    :root{--bg1:#0f172a;--bg2:#312e81;--card:rgba(255,255,255,.92);--border:rgba(15,23,42,.10);--text:#0f172a;--muted:rgba(15,23,42,.65);--primary:#4f46e5;--primary2:#4338ca;--success:#16a34a;--danger:#dc2626;--shadow:0 20px 50px rgba(0,0,0,.20);--shadow2:0 12px 30px rgba(0,0,0,.15);--radius:18px}
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;min-height:100vh;color:#e2e8f0;background:radial-gradient(1200px 600px at 10% 10%, rgba(99,102,241,.45), transparent 60%),radial-gradient(900px 600px at 90% 20%, rgba(14,165,233,.30), transparent 55%),linear-gradient(135deg,var(--bg1) 0%,var(--bg2) 100%)}
    .container{max-width:1200px;margin:0 auto;padding:28px 20px 48px}
    .topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px;border:1px solid rgba(255,255,255,.10);background:rgba(255,255,255,.06);backdrop-filter:blur(10px);border-radius:var(--radius);box-shadow:var(--shadow2);margin-bottom:18px}
    .brand{display:flex;flex-direction:column;gap:2px;min-width:0}
    .brand-title{font-weight:800;letter-spacing:-.02em;font-size:1.25rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .brand-subtitle{font-size:.95rem;color:rgba(226,232,240,.85);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .topbar-right{display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:flex-end}
    .pill{display:inline-flex;align-items:center;gap:10px;padding:10px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.07);color:rgba(226,232,240,.95);font-weight:800;font-size:.9rem}
    .pill-dot{width:10px;height:10px;border-radius:999px;background:#22c55e;box-shadow:0 0 0 6px rgba(34,197,94,.18);animation:pulse 2s infinite}
    .panel{background:var(--card);color:var(--text);border-radius:calc(var(--radius) + 2px);border:1px solid var(--border);box-shadow:var(--shadow);padding:22px}
    .panel-header{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}
    .panel-title{font-size:1.1rem;font-weight:900}
    .services-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px}
    .service-card{border:1px solid var(--border);border-radius:16px;padding:18px;background:rgba(255,255,255,.75);box-shadow:0 10px 22px rgba(15,23,42,.10);transition:transform .18s ease,box-shadow .18s ease;min-width:0;overflow:hidden}
    .service-card:hover{transform:translateY(-2px);box-shadow:0 14px 28px rgba(15,23,42,.14)}
    .service-card.running{border-left:5px solid var(--success)}
    .service-card.stopped{border-left:5px solid var(--danger)}
    .service-header{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
    .service-name{font-size:1.05rem;font-weight:900;letter-spacing:-.01em}
    .status-pill{display:inline-flex;align-items:center;gap:8px;padding:8px 10px;border-radius:999px;font-weight:900;font-size:.85rem;border:1px solid var(--border)}
    .status-pill.running{background:rgba(22,163,74,.10);color:#166534}
    .status-pill.stopped{background:rgba(220,38,38,.10);color:#7f1d1d}
    .status-pill .dot{width:9px;height:9px;border-radius:999px;background:currentColor;opacity:.9}
    .service-info{display:grid;grid-template-columns:1fr;gap:8px;margin-bottom:14px}
    .info-item{display:flex;justify-content:space-between;gap:10px;font-size:.92rem}
    .info-label{color:var(--muted);font-weight:800}
    .info-value{color:var(--text);font-weight:900;text-align:right;overflow-wrap:anywhere}
    .service-link{display:inline-flex;align-items:center;gap:8px;padding:10px 12px;border-radius:12px;background:linear-gradient(135deg,var(--primary) 0%,var(--primary2) 100%);color:#fff;text-decoration:none;font-weight:900;box-shadow:0 10px 18px rgba(79,70,229,.20);transition:transform .18s ease,box-shadow .18s ease;margin-bottom:12px}
    .service-link:hover{transform:translateY(-1px);box-shadow:0 14px 26px rgba(79,70,229,.25)}
    .service-actions{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
    .btn{padding:11px 10px;border:1px solid var(--border);border-radius:12px;font-weight:900;font-size:.92rem;cursor:pointer;transition:transform .12s ease,box-shadow .12s ease,background .12s ease;display:inline-flex;justify-content:center;align-items:center;gap:8px;background:rgba(255,255,255,.75);min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .btn:hover{transform:translateY(-1px);box-shadow:0 12px 22px rgba(15,23,42,.12)}
    .btn:disabled{opacity:.5;cursor:not-allowed;transform:none;box-shadow:none}
    .btn-start{background:rgba(22,163,74,.12);color:#166534}
    .btn-stop{background:rgba(220,38,38,.12);color:#7f1d1d}
    .btn-restart{background:rgba(245,158,11,.12);color:#7c2d12}
    .message{position:fixed;top:18px;right:18px;padding:14px 16px;border-radius:14px;color:#fff;font-weight:900;font-size:.95rem;z-index:1000;animation:slideIn .25s ease;box-shadow:0 18px 40px rgba(0,0,0,.25)}
    .message.success{background:linear-gradient(135deg,var(--success) 0%,#15803d 100%)}
    .message.error{background:linear-gradient(135deg,var(--danger) 0%,#b91c1c 100%)}
    .refresh-btn{position:fixed;bottom:22px;right:22px;width:56px;height:56px;border-radius:999px;background:linear-gradient(135deg,var(--primary) 0%,var(--primary2) 100%);color:#fff;border:none;font-size:1.35rem;cursor:pointer;box-shadow:0 18px 40px rgba(79,70,229,.35);transition:transform .15s ease;display:flex;align-items:center;justify-content:center}
    .refresh-btn:hover{transform:rotate(180deg)}
    @keyframes slideIn{from{transform:translateX(10px);opacity:0}to{transform:translateX(0);opacity:1}}
    @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
    @media (max-width:780px){.topbar{flex-direction:column;align-items:stretch}.topbar-right{justify-content:flex-start}.services-grid{grid-template-columns:1fr}.service-actions{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"topbar\">
      <div class=\"brand\">
        <div class=\"brand-title\">🏫 Theodor-Litt-Schule · Docker Dienste</div>
        <div class=\"brand-subtitle\">Live-Status & Steuerung (lokal)</div>
      </div>
      <div class=\"topbar-right\">
        <div class=\"pill\"><span class=\"pill-dot\"></span><span>Live</span></div>
        <button class=\"btn btn-start\" onclick=\"startAllServices()\"><span>🚀</span><span>Alle starten</span></button>
        <button class=\"btn btn-stop\" onclick=\"stopAllServices()\"><span>⏹️</span><span>Alle stoppen</span></button>
      </div>
    </div>

    <div class=\"panel\">
      <div class=\"panel-header\">
        <div class=\"panel-title\">Service-Status</div>
        <div style=\"color: rgba(15,23,42,0.65); font-weight: 900; font-size: 0.92rem;\">Aktualisiert alle 15 Sekunden</div>
      </div>
      <div class=\"services-grid\" id=\"servicesGrid\"></div>
    </div>
  </div>

  <button class=\"refresh-btn\" onclick=\"loadServices()\" title=\"Aktualisieren\">🔄</button>

  <script>
    function showMessage(message, type) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${type || 'success'}`;
      messageDiv.textContent = message;
      document.body.appendChild(messageDiv);
      setTimeout(() => {
        messageDiv.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => messageDiv.remove(), 300);
      }, 3000);
    }

    async function loadServices() {
      try {
        const response = await fetch('/api/services');
        const services = await response.json();
        const grid = document.getElementById('servicesGrid');
        grid.innerHTML = '';
        services.forEach((service) => {
          const card = document.createElement('div');
          card.className = `service-card ${service.state}`;

          const statusClass = service.state === 'running' ? 'running' : 'stopped';
          const statusText = service.state === 'running' ? 'Läuft' : 'Gestoppt';

          let urlHtml = '';
          if (service.url && service.state === 'running') {
            urlHtml = `
              <div class=\"service-url\">
                <a href=\"${service.url}\" target=\"_blank\" class=\"service-link\">
                  <span>🔗</span><span>Öffnen</span>
                </a>
              </div>
            `;
          }

          card.innerHTML = `
            <div class=\"service-header\">
              <div class=\"service-name\">${service.icon || '📦'} ${service.display_name || service.name}</div>
              <div class=\"status-pill ${statusClass}\"><span class=\"dot\"></span><span>${statusText}</span></div>
            </div>
            <div class=\"service-info\">
              <div class=\"info-item\"><span class=\"info-label\">Image:</span><span class=\"info-value\">${service.image}</span></div>
              <div class=\"info-item\"><span class=\"info-label\">Port:</span><span class=\"info-value\">${(service.ports || []).join(', ') || 'Keine'}</span></div>
              <div class=\"info-item\"><span class=\"info-label\">Container:</span><span class=\"info-value\">${service.container_name}</span></div>
            </div>
            ${urlHtml}
            <div class=\"service-actions\">
              <button class=\"btn btn-start\" onclick=\"startService('${service.container_name}')\" ${service.state === 'running' ? 'disabled' : ''}><span>▶️</span><span>Starten</span></button>
              <button class=\"btn btn-stop\" onclick=\"stopService('${service.container_name}')\" ${service.state !== 'running' ? 'disabled' : ''}><span>⏹️</span><span>Stoppen</span></button>
              <button class=\"btn btn-restart\" onclick=\"restartService('${service.container_name}')\" ${service.state !== 'running' ? 'disabled' : ''}><span>🔄</span><span>Neustart</span></button>
            </div>
          `;
          grid.appendChild(card);
        });
      } catch (error) {
        showMessage('Fehler beim Laden der Dienste: ' + error.message, 'error');
      }
    }

    async function startAllServices() {
      try {
        showMessage('Starte alle Dienste...', 'success');
        const response = await fetch('/api/start-all', { method: 'POST' });
        const result = await response.json();
        showMessage(result.message, result.success ? 'success' : 'error');
        setTimeout(loadServices, 2000);
      } catch (error) {
        showMessage('Fehler: ' + error.message, 'error');
      }
    }

    async function stopAllServices() {
      try {
        showMessage('Stoppe alle Dienste...', 'success');
        const response = await fetch('/api/stop-all', { method: 'POST' });
        const result = await response.json();
        showMessage(result.message, result.success ? 'success' : 'error');
        setTimeout(loadServices, 2000);
      } catch (error) {
        showMessage('Fehler: ' + error.message, 'error');
      }
    }

    async function startService(serviceName) {
      try {
        const response = await fetch(`/api/start/${serviceName}`, { method: 'POST' });
        const result = await response.json();
        showMessage(result.message, result.success ? 'success' : 'error');
        setTimeout(loadServices, 1500);
      } catch (error) {
        showMessage('Fehler: ' + error.message, 'error');
      }
    }

    async function stopService(serviceName) {
      try {
        const response = await fetch(`/api/stop/${serviceName}`, { method: 'POST' });
        const result = await response.json();
        showMessage(result.message, result.success ? 'success' : 'error');
        setTimeout(loadServices, 1500);
      } catch (error) {
        showMessage('Fehler: ' + error.message, 'error');
      }
    }

    async function restartService(serviceName) {
      try {
        const response = await fetch(`/api/restart/${serviceName}`, { method: 'POST' });
        const result = await response.json();
        showMessage(result.message, result.success ? 'success' : 'error');
        setTimeout(loadServices, 1500);
      } catch (error) {
        showMessage('Fehler: ' + error.message, 'error');
      }
    }

    setInterval(loadServices, 15000);
    loadServices();
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/services")
def api_services():
    try:
        return jsonify(_services())
    except Exception as e:
        return jsonify([])


@app.route("/api/start/<service_name>", methods=["POST"])
def api_start(service_name):
    success, message = _start(service_name)
    return jsonify({"success": success, "message": message})


@app.route("/api/stop/<service_name>", methods=["POST"])
def api_stop(service_name):
    success, message = _stop(service_name)
    return jsonify({"success": success, "message": message})


@app.route("/api/restart/<service_name>", methods=["POST"])
def api_restart(service_name):
    success, message = _restart(service_name)
    return jsonify({"success": success, "message": message})


@app.route("/api/start-all", methods=["POST"])
def api_start_all():
    try:
        managed = _compose_containers()
        started = 0
        for c in managed:
            if c.status != "running":
                try:
                    c.start()
                    started += 1
                except Exception:
                    pass
        return jsonify({"success": True, "message": f"Dienste gestartet: {started}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Fehler: {str(e)}"})


@app.route("/api/stop-all", methods=["POST"])
def api_stop_all():
    try:
        managed = _compose_containers()
        stopped = 0
        for c in managed:
            if c.status == "running":
                try:
                    c.stop(timeout=30)
                    stopped += 1
                except Exception:
                    pass
        return jsonify({"success": True, "message": f"Dienste gestoppt: {stopped}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Fehler: {str(e)}"})


def start_web_interface():
    def run_app():
        app.run(host="0.0.0.0", port=3000, debug=False, use_reloader=False)

    thread = threading.Thread(target=run_app, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    start_web_interface()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)
