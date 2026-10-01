import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager

STATUS_FILE = BASE_DIR / "data" / "live_production_status.json"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Naughty Duo — Autonomous Control Center</title>
    <style>
        :root {
            --bg: #0b1120;
            --card: #1e293b;
            --card-border: #334155;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.2);
            --text: #f8fafc;
            --muted: #94a3b8;
            --success: #22c55e;
            --warning: #eab308;
            --danger: #ef4444;
            --yt-color: #ff0000;
            --tt-color: #00f2fe;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }
        h1 { margin: 0; font-size: 24px; color: var(--accent); letter-spacing: -0.5px; }
        .badge {
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .badge-live {
            background: rgba(34, 197, 94, 0.15);
            color: var(--success);
            border: 1px solid rgba(34, 197, 94, 0.4);
        }
        .badge-yt {
            background: rgba(255, 0, 0, 0.15);
            color: #ff4d4d;
            border: 1px solid rgba(255, 0, 0, 0.4);
        }
        .badge-tt {
            background: rgba(0, 242, 254, 0.15);
            color: #00f2fe;
            border: 1px solid rgba(0, 242, 254, 0.4);
        }
        .badge-both {
            background: linear-gradient(90deg, rgba(255,0,0,0.15), rgba(0,242,254,0.15));
            color: #ffffff;
            border: 1px solid #38bdf8;
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 8px var(--success);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.3); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        /* LIVE PRODUCTION HERO CARD */
        .hero-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 2px solid var(--accent);
            box-shadow: 0 0 25px var(--accent-glow);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }
        .hero-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        .hero-title {
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
            margin: 6px 0;
        }
        .hero-meta {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            font-size: 13px;
            color: var(--muted);
            margin: 12px 0 18px 0;
        }
        .hero-meta span strong {
            color: var(--accent);
        }
        .progress-box {
            background: #0f172a;
            border-radius: 9999px;
            height: 24px;
            width: 100%;
            overflow: hidden;
            border: 1px solid var(--card-border);
            position: relative;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #38bdf8, #22c55e);
            border-radius: 9999px;
            transition: width 0.6s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 12px;
            font-size: 12px;
            font-weight: 800;
            color: #0f172a;
        }
        .progress-text {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            color: var(--muted);
            margin-top: 8px;
            font-weight: 600;
        }

        /* LIVE DIAGNOSTICS & DELAY REASON BANNER */
        .delay-banner {
            margin-top: 16px;
            padding: 12px 16px;
            border-radius: 8px;
            background: rgba(30, 41, 59, 0.7);
            border-left: 4px solid var(--accent);
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
        }
        .delay-banner.alert {
            border-left-color: var(--warning);
            background: rgba(234, 179, 8, 0.1);
        }
        .delay-banner strong {
            color: #ffffff;
        }

        /* STATS GRID */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 18px;
            margin-bottom: 24px;
        }
        .card {
            background: var(--card);
            border-radius: 10px;
            padding: 18px;
            border: 1px solid var(--card-border);
        }
        .card h3 {
            margin: 0;
            font-size: 12px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-val {
            font-size: 24px;
            font-weight: 800;
            color: var(--text);
            margin: 8px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th, td {
            text-align: left;
            padding: 10px 10px;
            border-bottom: 1px solid var(--card-border);
        }
        th {
            color: var(--muted);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        code {
            background: #0f172a;
            padding: 3px 6px;
            border-radius: 4px;
            color: var(--accent);
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>The Naughty Duo — Autonomous Content Operations Engine</h1>
            <p style="color: var(--muted); margin: 5px 0 0 0; font-size: 13px;">Auto-Pilot Production Matrix | Multi-Platform Distribution Locked</p>
        </div>
        <div>
            <span class="badge badge-live">
                <span class="pulse-dot"></span> System Online & Real-time Auto-Sync
            </span>
        </div>
    </div>

    <!-- LIVE CURRENT RUNNING EPISODE CARD -->
    <div class="hero-card" id="hero-card">
        <div class="hero-top">
            <div style="display: flex; gap: 8px; align-items: center;">
                <span class="badge badge-live" style="background: rgba(56, 189, 248, 0.2); color: var(--accent); border-color: var(--accent);">
                    <span class="pulse-dot" style="background: var(--accent); box-shadow: 0 0 8px var(--accent);"></span>
                    CURRENTLY ACTIVE GENERATION
                </span>
                <span id="hero-platform-badge" class="badge badge-both">__PLATFORM_BADGE__</span>
            </div>
            <span id="hero-stage" style="color: var(--warning); font-weight: 700; font-size: 14px;">__STAGE__</span>
        </div>
        <div class="hero-title" id="hero-title">__ACTIVE_TITLE__</div>
        <div class="hero-meta">
            <span>Episode ID: <strong id="hero-id">__ACTIVE_ID__</strong></span>
            <span>Account Slot: <strong id="hero-account">__ACTIVE_ACCOUNT__</strong></span>
            <span>Target Platform: <strong id="hero-platform">__ACTIVE_PLATFORM__</strong></span>
            <span>Current Scene: <strong id="hero-scene">__ACTIVE_SCENE__</strong></span>
            <span>Project Lock: <strong style="color: var(--success);">The Naughty Duo</strong></span>
        </div>
        <div class="progress-box">
            <div class="progress-bar" id="hero-bar" style="width: __PERCENT__%;">__PERCENT__%</div>
        </div>
        <div class="progress-text">
            <span id="hero-parts-text">__PARTS_TEXT__</span>
            <span id="hero-percent-label">__PERCENT__% Completed</span>
        </div>

        <!-- GENERATION DELAY & BOTTLENECK DIAGNOSTICS BOX -->
        <div class="delay-banner" id="delay-box">
            <div>
                <span style="color: var(--muted); margin-right: 8px;">⏱️ Generation Status / Diagnostics:</span>
                <strong id="delay-text">__DELAY_REASON__</strong>
            </div>
            <span id="delay-tag" class="badge" style="background: rgba(255,255,255,0.06); color: var(--accent);">Real-Time Watchdog</span>
        </div>
    </div>

    <!-- STATS -->
    <div class="grid">
        <div class="card">
            <h3>Active Queue</h3>
            <div class="stat-val">__QUEUED_COUNT__ Stories</div>
            <p style="color: var(--muted); font-size: 12px; margin: 0;">Unreleased Episodes: <strong style="color: var(--accent);">10 Fresh</strong></p>
        </div>
        <div class="card">
            <h3>YouTube Distribution</h3>
            <div class="stat-val" style="color: #ff4d4d;">__YT_JOBS_COUNT__ Queued</div>
            <p style="color: var(--muted); font-size: 12px; margin: 0;">Format: <strong>Vertical Shorts (35-45s)</strong></p>
        </div>
        <div class="card">
            <h3>TikTok Distribution</h3>
            <div class="stat-val" style="color: #00f2fe;">__TT_JOBS_COUNT__ Queued</div>
            <p style="color: var(--muted); font-size: 12px; margin: 0;">Format: <strong>Creator Rewards (60s+)</strong></p>
        </div>
        <div class="card">
            <h3>Zero Duplicate Guard</h3>
            <div class="stat-val" style="color: var(--success);">__INDEXED_COUNT__ Indexed</div>
            <p style="color: var(--muted); font-size: 12px; margin: 0;">YouTube + TikTok: <strong style="color: var(--success);">0% Duplicates Lock</strong></p>
        </div>
        <div class="card">
            <h3>Google Flow Pool</h3>
            <div class="stat-val">__ACCOUNTS_COUNT__ Accounts</div>
            <p style="color: var(--muted); font-size: 12px; margin: 0;">Project Lock: <strong style="color: var(--success);">The Naughty Duo</strong></p>
        </div>
        <div class="card">
            <h3>Total Daily Credits</h3>
            <div class="stat-val" style="color: #a855f7;">__TOTAL_CREDITS__ Credits</div>
            <p style="color: var(--muted); font-size: 12px; margin: 0;">Across All 8 ID Slots</p>
        </div>
    </div>

    <!-- CONTENT QUEUE TABLE WITH TARGET PLATFORMS -->
    <div class="card" style="margin-bottom: 24px;">
        <h3>Production Pipeline Queue — Platform Distribution Targets</h3>
        <table>
            <thead>
                <tr>
                    <th>Story ID</th>
                    <th>Title</th>
                    <th>Target Platforms</th>
                    <th>Duration Target</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Scenes Progress</th>
                </tr>
            </thead>
            <tbody id="stories-body">
                __STORIES_TABLE__
            </tbody>
        </table>
    </div>

    <!-- ACCOUNTS TABLE WITH CREDITS BREAKDOWN -->
    <div class="card">
        <h3>Google Flow Accounts — Live Credits & Quota Breakdown</h3>
        <table>
            <thead>
                <tr>
                    <th>Slot</th>
                    <th>Google Account (Email)</th>
                    <th>Tier</th>
                    <th>Total Available Credits</th>
                    <th>Locked Project</th>
                    <th>Account Status</th>
                </tr>
            </thead>
            <tbody id="accounts-body">
                __ACCOUNTS_TABLE__
            </tbody>
        </table>
    </div>

    <!-- REAL-TIME LIVE POLLING & AUTO-REFRESH SCRIPT -->
    <script>
        let secondsLeft = 60;
        function updateTimer() {
            secondsLeft--;
            const timerEl = document.getElementById('auto-refresh-timer');
            if (timerEl) {
                timerEl.innerText = `Auto-refresh in ${secondsLeft}s`;
            }
            if (secondsLeft <= 0) {
                location.reload();
            }
        }
        setInterval(updateTimer, 1000);

        async function updateLiveStatus() {
            try {
                const res = await fetch('/api/live_state');
                if (!res.ok) return;
                const data = await res.json();
                
                if (data.active_title) {
                    document.getElementById('hero-title').innerText = data.active_title;
                    document.getElementById('hero-id').innerText = data.active_id;
                    document.getElementById('hero-account').innerText = data.active_account;
                    document.getElementById('hero-scene').innerText = data.active_scene;
                    document.getElementById('hero-stage').innerText = data.stage;
                    
                    if (data.target_platform) {
                        document.getElementById('hero-platform').innerText = data.target_platform;
                        document.getElementById('hero-platform-badge').innerText = data.target_platform;
                    }
                    if (data.delay_reason) {
                        document.getElementById('delay-text').innerText = data.delay_reason;
                        const dBox = document.getElementById('delay-box');
                        if (data.delay_reason.toLowerCase().includes('close brave') || data.delay_reason.toLowerCase().includes('alert') || data.delay_reason.toLowerCase().includes('timed out')) {
                            dBox.classList.add('alert');
                        } else {
                            dBox.classList.remove('alert');
                        }
                    }

                    const pct = data.percentage || 0;
                    const bar = document.getElementById('hero-bar');
                    bar.style.width = pct + '%';
                    bar.innerText = pct + '%';
                    
                    document.getElementById('hero-parts-text').innerText = data.parts_text;
                    document.getElementById('hero-percent-label').innerText = pct + '% Completed';
                }
            } catch(e) {}
        }
        setInterval(updateLiveStatus, 2000);
    </script>
</body>
</html>
"""

def get_current_live_state():
    """Reads live progress state from file or infers from DB."""
    data = {}
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    # Ensure defaults if keys missing
    data.setdefault("target_platform", "YouTube Shorts & TikTok")
    
    # Check if brave.exe is currently open by USER (interactive window)
    # Background automation runs brave with --remote-debugging-pipe or --headless, which should NOT trigger this alert
    import psutil
    user_brave_open = False
    for p in psutil.process_iter(['name', 'cmdline']):
        try:
            if p.info['name'] and p.info['name'].lower() == 'brave.exe':
                cmdline = " ".join(p.info.get('cmdline') or [])
                # If it does NOT contain automation flags and is a main browser process (not renderer/utility/crashpad)
                if "--type=" not in cmdline and "--remote-debugging-pipe" not in cmdline and "AutomationControlled" not in cmdline:
                    user_brave_open = True
                    break
        except Exception:
            pass

    if user_brave_open:
        data["delay_reason"] = "⚠️ Brave Browser window is OPEN by user. Background automation will resume once Brave window is closed."
    else:
        # If no specific delay from engine, show normal active status
        if "delay_reason" not in data or "Brave Browser is OPEN" in data.get("delay_reason", ""):
            data["delay_reason"] = "🟢 Normal Operation: Brave session active, dispatching scene prompt to Google Flow."

    if data.get("active_title"):
        return data

    # Infer from DB
    db = DatabaseManager()
    with db.get_connection() as conn:
        active_story = conn.execute("""
            SELECT s.*, 
                (SELECT COUNT(*) FROM story_parts WHERE story_id = s.id AND status = 'COMPLETED') as done_parts,
                (SELECT COUNT(*) FROM story_parts WHERE story_id = s.id) as total_parts
            FROM stories s
            WHERE s.state IN ('GENERATING', 'PARTIAL', 'COMPLETING')
            ORDER BY s.priority ASC, s.updated_at DESC
            LIMIT 1
        """).fetchone()

        if not active_story:
            active_story = conn.execute("SELECT s.*, 0 as done_parts, 3 as total_parts FROM stories s WHERE s.state = 'QUEUED' ORDER BY priority ASC LIMIT 1").fetchone()

        if active_story:
            done = active_story["done_parts"]
            total = max(active_story["total_parts"], 3)
            pct = int((done / total) * 100) if total > 0 else 0
            
            # Find generating part
            active_part = conn.execute("""
                SELECT p.part_number, p.scene_label, p.assigned_account_id, a.email
                FROM story_parts p
                LEFT JOIN accounts a ON p.assigned_account_id = a.id
                WHERE p.story_id = ? AND p.status IN ('GENERATING', 'PENDING')
                ORDER BY p.part_number ASC LIMIT 1
            """, (active_story["id"],)).fetchone()

            slot_str = "/u/0/ (TecHWirE9999@gmail.com)"
            scene_str = "Scene 1 of 3: Hook"
            if active_part:
                acc_email = active_part["email"] or "TecHWirE9999@gmail.com"
                slot_id = active_part["assigned_account_id"] or "acc_0"
                slot_num = slot_id.replace("acc_", "")
                slot_str = f"/u/{slot_num}/ ({acc_email})"
                scene_str = f"Scene {active_part['part_number']} of {total}: {active_part['scene_label']}"

            stage = "Rendering in Google Flow..." if active_story["state"] in ("GENERATING", "PARTIAL") else "Assembling Final Video..."
            if done == 0 and active_story["state"] == "QUEUED":
                stage = "Queued for Generation"

            data.update({
                "active_id": active_story["id"],
                "active_title": active_story["title"],
                "active_account": slot_str,
                "active_scene": scene_str,
                "percentage": max(pct, 15 if active_story["state"] == "GENERATING" else 0),
                "parts_text": f"{done} of {total} Scenes Done",
                "stage": stage,
                "target_platform": "YouTube Shorts & TikTok"
            })
            return data

    return {
        "active_id": "ep_18_magic_freeze_remote",
        "active_title": "Mummy Ka Magic Remote! 🎮😂 Sab Freeze Ho Gaye! #TheNaughtyDuo #shorts",
        "active_account": "/u/0/ (TecHWirE9999@gmail.com)",
        "active_scene": "Scene 1 of 3: Hook (Magic Freeze Remote)",
        "percentage": 0,
        "parts_text": "0 of 3 Scenes Done",
        "stage": "Brand New Fresh Episode Queued",
        "target_platform": "YouTube Shorts & TikTok",
        "delay_reason": "🟢 Normal Operation: Standing by for execution cycle."
    }

class ControlCenterHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress console emoji encoding warnings on Windows

    def do_GET(self):
        if self.path == "/api/live_state":
            data = get_current_live_state()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if self.path == "/api/sync_platforms":
            from backend.services.cross_platform_scanner import CrossPlatformScanner
            scanner = CrossPlatformScanner()
            stats = scanner.sync_all_platforms()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode("utf-8"))
            return

        db = DatabaseManager()
        with db.get_connection() as conn:
            query = """
                SELECT s.*,
                       (SELECT COUNT(*) FROM story_parts WHERE story_id = s.id AND status = 'COMPLETED') as done_parts,
                       (SELECT COUNT(*) FROM story_parts WHERE story_id = s.id) as total_parts_db,
                       GROUP_CONCAT(DISTINCT p.platform) as platforms
                FROM stories s
                LEFT JOIN publishing_jobs p ON s.id = p.story_id
                WHERE s.state != 'PUBLISHED'
                GROUP BY s.id
                ORDER BY s.priority ASC, s.created_at DESC
                LIMIT 15
            """
            stories = conn.execute(query).fetchall()
            accounts = conn.execute("SELECT * FROM accounts ORDER BY slot_index ASC").fetchall()
            indexed_count = conn.execute("SELECT COUNT(*) as c FROM platform_indexed_videos").fetchone()["c"]
            yt_jobs_count = conn.execute("SELECT COUNT(*) as c FROM publishing_jobs WHERE platform = 'YOUTUBE' AND status = 'PENDING'").fetchone()["c"]
            tt_jobs_count = conn.execute("SELECT COUNT(*) as c FROM publishing_jobs WHERE platform = 'TIKTOK' AND status = 'PENDING'").fetchone()["c"]

            stories_html = ""
            for s in stories:
                done = s["done_parts"]
                total = s["total_parts_db"] or s["total_parts"]
                state_color = "#22c55e" if s["state"] == "COMPLETED" else ("#38bdf8" if s["state"] == "GENERATING" else "#94a3b8")
                
                # Render platforms badge
                plats = s["platforms"] or "YOUTUBE,TIKTOK"
                plat_badges = ""
                if "YOUTUBE" in plats:
                    plat_badges += "<span class='badge badge-yt'>YouTube</span> "
                if "TIKTOK" in plats:
                    plat_badges += "<span class='badge badge-tt'>TikTok</span>"

                target_dur = f"{s['target_duration_seconds']}s" if s['target_duration_seconds'] else "60-70s"

                stories_html += f"""<tr>
                    <td><code>{s['id']}</code></td>
                    <td>{s['title'][:50]}...</td>
                    <td>{plat_badges}</td>
                    <td><strong>{target_dur}</strong></td>
                    <td><span class='badge' style='background: rgba(255,255,255,0.08); color: {state_color};'>{s['state']}</span></td>
                    <td>P{s['priority']}</td>
                    <td><strong>{done}/{total} Scenes</strong></td>
                </tr>"""

            accounts_html = ""
            total_credits = 0
            for a in accounts:
                creds = a["available_credits"] if "available_credits" in a.keys() and a["available_credits"] is not None else 50
                total_credits += creds
                tier_badge = f"<span class='badge' style='background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4);'>{a['tier']}</span>" if a['tier'] == 'PRO' else f"<span class='badge' style='background: rgba(255, 255, 255, 0.08); color: var(--muted);'>{a['tier']}</span>"
                creds_badge = f"<strong style='color: #c084fc; font-size: 14px;'>{creds} Credits</strong>" if a['tier'] == 'PRO' else f"<strong style='color: #38bdf8; font-size: 14px;'>{creds} Credits</strong>"
                status_color = "#22c55e" if a['status'] == 'ACTIVE' else "#eab308"
                accounts_html += f"""<tr>
                    <td><code>/u/{a['slot_index']}/</code></td>
                    <td><strong>{a['email']}</strong></td>
                    <td>{tier_badge}</td>
                    <td>{creds_badge}</td>
                    <td><span style='color: #22c55e; font-weight: 600;'>The Naughty Duo</span></td>
                    <td><span style='color: {status_color}; font-weight: 600;'>{a['status']}</span></td>
                </tr>"""

        live = get_current_live_state()

        content = HTML_TEMPLATE
        content = content.replace("__ACTIVE_TITLE__", live["active_title"])
        content = content.replace("__ACTIVE_ID__", live["active_id"])
        content = content.replace("__ACTIVE_ACCOUNT__", live["active_account"])
        content = content.replace("__ACTIVE_SCENE__", live["active_scene"])
        content = content.replace("__STAGE__", live["stage"])
        content = content.replace("__PERCENT__", str(live["percentage"]))
        content = content.replace("__PARTS_TEXT__", live["parts_text"])
        content = content.replace("__ACTIVE_PLATFORM__", live.get("target_platform", "YouTube & TikTok"))
        content = content.replace("__PLATFORM_BADGE__", live.get("target_platform", "YouTube & TikTok"))
        content = content.replace("__DELAY_REASON__", live.get("delay_reason", "Normal Operation"))

        content = content.replace("__QUEUED_COUNT__", str(len(stories)))
        content = content.replace("__YT_JOBS_COUNT__", str(yt_jobs_count))
        content = content.replace("__TT_JOBS_COUNT__", str(tt_jobs_count))
        content = content.replace("__INDEXED_COUNT__", str(indexed_count))
        content = content.replace("__ACCOUNTS_COUNT__", str(len(accounts)))
        content = content.replace("__TOTAL_CREDITS__", str(total_credits))
        content = content.replace("__STORIES_TABLE__", stories_html or "<tr><td colspan='7'>No stories in queue</td></tr>")
        content = content.replace("__ACCOUNTS_TABLE__", accounts_html or "<tr><td colspan='6'>No accounts configured</td></tr>")

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
