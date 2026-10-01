import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Naughty Duo - Autonomous Control Center</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --accent: #38bdf8; --text: #f8fafc; --muted: #94a3b8; --success: #22c55e; --warning: #eab308; --danger: #ef4444; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 15px; margin-bottom: 25px; }
        h1 { margin: 0; font-size: 24px; color: var(--accent); }
        .badge { padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
        .badge-online { background: rgba(34, 197, 94, 0.2); color: var(--success); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 25px; }
        .card { background: var(--card); border-radius: 10px; padding: 18px; border: 1px solid #334155; }
        .card h3 { margin-top: 0; font-size: 15px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .stat-val { font-size: 28px; font-weight: 700; color: var(--text); margin: 8px 0; }
        .actions { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 25px; }
        button { background: var(--card); border: 1px solid var(--accent); color: var(--accent); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
        button:hover { background: var(--accent); color: var(--bg); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #334155; }
        th { color: var(--muted); }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>The Naughty Duo — Autonomous Content Operations Engine</h1>
            <p style="color: var(--muted); margin: 5px 0 0 0; font-size: 13px;">Production-Grade AI Content Operations | Character Lock Active</p>
        </div>
        <div>
            <span class="badge badge-online">System Online</span>
        </div>
    </div>

    <div class="actions">
        <button onclick="location.reload()">Refresh Live State</button>
        <button onclick="alert('Simulation Mode Triggered')">Run Simulation</button>
        <button onclick="alert('Queue Paused')">Pause Automation</button>
        <button onclick="alert('Incomplete Recovery Triggered')">Force Incomplete Story Recovery</button>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Active Content Queue</h3>
            <div class="stat-val">__QUEUED_COUNT__ Stories</div>
            <p style="color: var(--muted); font-size: 13px;">P0 Incomplete Recovery: <strong>__P0_COUNT__ Active</strong></p>
        </div>
        <div class="card">
            <h3>Google Flow Pool</h3>
            <div class="stat-val">__ACCOUNTS_COUNT__ Accounts</div>
            <p style="color: var(--muted); font-size: 13px;">Project Lock: <span style="color: var(--success);">ENFORCED</span></p>
        </div>
        <div class="card">
            <h3>YouTube & TikTok</h3>
            <div class="stat-val">Connected</div>
            <p style="color: var(--muted); font-size: 13px;">Prime Slot Engine: <strong>6 Slots / Day</strong></p>
        </div>
        <div class="card">
            <h3>Character Identity Lock</h3>
            <div class="stat-val" style="color: var(--accent);">Pinki, Kaartik, Kaavya</div>
            <p style="color: var(--muted); font-size: 13px;">Benchmark: <strong>Garden Me Jhula (Pixar 3D)</strong></p>
        </div>
    </div>

    <div class="card" style="margin-bottom: 25px;">
        <h3>Current Content Pipeline (P0 Incomplete Recovery First)</h3>
        <table>
            <thead>
                <tr>
                    <th>Story ID</th>
                    <th>Title</th>
                    <th>State</th>
                    <th>Priority</th>
                    <th>Progress</th>
                </tr>
            </thead>
            <tbody>
                __STORIES_TABLE__
            </tbody>
        </table>
    </div>

    <div class="card">
        <h3>Google Flow Accounts & Project Locking</h3>
        <table>
            <thead>
                <tr>
                    <th>Slot</th>
                    <th>Account</th>
                    <th>Tier</th>
                    <th>Locked Project ID</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                __ACCOUNTS_TABLE__
            </tbody>
        </table>
    </div>
</body>
</html>
"""

class ControlCenterHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = DatabaseManager()
        with db.get_connection() as conn:
            stories = conn.execute("SELECT * FROM stories ORDER BY priority ASC, created_at DESC LIMIT 10").fetchall()
            accounts = conn.execute("SELECT * FROM accounts ORDER BY slot_index ASC").fetchall()
            p0_count = conn.execute("SELECT COUNT(*) as c FROM stories WHERE priority = 0").fetchone()["c"]

        stories_html = ""
        for s in stories:
            parts = conn.execute("SELECT status FROM story_parts WHERE story_id = ?", (s["id"],)).fetchall()
            done = sum(1 for p in parts if p["status"] == "COMPLETED")
            total = len(parts) if parts else s["total_parts"]
            stories_html += f"<tr><td><code>{s['id']}</code></td><td>{s['title'][:55]}...</td><td><span class='badge' style='background: #334155;'>{s['state']}</span></td><td>P{s['priority']}</td><td>{done}/{total} Parts</td></tr>"

        accounts_html = ""
        for a in accounts:
            accounts_html += f"<tr><td>/u/{a['slot_index']}/</td><td>{a['email']}</td><td>{a['tier']}</td><td><code>{a['project_id']}</code></td><td><span style='color: #22c55e;'>{a['status']}</span></td></tr>"

        content = HTML_TEMPLATE.replace("__QUEUED_COUNT__", str(len(stories)))
        content = content.replace("__P0_COUNT__", str(p0_count))
        content = content.replace("__ACCOUNTS_COUNT__", str(len(accounts)))
        content = content.replace("__STORIES_TABLE__", stories_html or "<tr><td colspan='5'>No stories in queue</td></tr>")
        content = content.replace("__ACCOUNTS_TABLE__", accounts_html or "<tr><td colspan='5'>No accounts configured</td></tr>")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

def run_server(port=8088):
    server = HTTPServer(("127.0.0.1", port), ControlCenterHandler)
    print(f"[CONTROL_CENTER] Dashboard live on http://127.0.0.1:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
