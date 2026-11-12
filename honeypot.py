"""
Simple Honeypot: fake SSH banner listener + HTTP request logger + local dashboard.
For authorized, isolated lab/academic use only.
"""
import csv
import html
import os
import socket
import sqlite3
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get("HONEYPOT_HOST", "127.0.0.1")
SSH_PORT = int(os.environ.get("SSH_PORT", "2222"))
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8080"))

# Render dashboard configuration
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = int(os.environ.get("PORT", os.environ.get("DASHBOARD_PORT", "5000")))

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "honeypot_logs.db")
LOCK = threading.Lock()


def now():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def init_db():
    with sqlite3.connect(DB_FILE) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            service TEXT NOT NULL,
            method TEXT,
            path TEXT,
            details TEXT
        )""")


def log_event(ip, service, method="", path="", details=""):
    with LOCK, sqlite3.connect(DB_FILE) as db:
        db.execute(
            "INSERT INTO events(timestamp,source_ip,service,method,path,details) VALUES(?,?,?,?,?,?)",
            (now(), ip, service, method[:20], path[:300], details[:300])
        )


def ssh_server():
    """Fake SSH-like banner listener; not a real SSH login server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, SSH_PORT))
    server.listen(50)
    print(f"[SSH honeypot] Listening on {HOST}:{SSH_PORT}")

    while True:
        conn, addr = server.accept()
        ip = addr[0]
        log_event(ip, "SSH", details="TCP connection received; fake SSH banner sent")
        try:
            conn.settimeout(2)
            conn.sendall(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n")
            try:
                data = conn.recv(512)
                if data:
                    preview = data[:100].decode(
                        "utf-8", errors="replace"
                    ).replace("\r", " ").replace("\n", " ")
                    log_event(ip, "SSH", details="Client data: " + preview)
            except socket.timeout:
                pass
        except OSError:
            pass
        finally:
            conn.close()


class FakeHTTPHandler(BaseHTTPRequestHandler):
    def _record(self):
        ip = self.client_address[0]
        length = min(int(self.headers.get("Content-Length", "0") or 0), 512)
        body = self.rfile.read(length) if length else b""

        details = "User-Agent: " + self.headers.get("User-Agent", "unknown")[:120]
        if body:
            details += " | Body bytes received: " + str(len(body))

        log_event(ip, "HTTP", self.command, self.path, details)

        page = b"""<!doctype html><html><head><title>Welcome</title></head>
        <body><h2>Welcome</h2><p>Service temporarily unavailable.</p></body></html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    do_GET = _record
    do_POST = _record
    do_HEAD = _record
    do_PUT = _record
    do_DELETE = _record

    def log_message(self, fmt, *args):
        return


def query_events(limit=100):
    with sqlite3.connect(DB_FILE) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def dashboard_html():
    rows = query_events(100)

    with sqlite3.connect(DB_FILE) as db:
        total = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        unique = db.execute(
            "SELECT COUNT(DISTINCT source_ip) FROM events"
        ).fetchone()[0]
        ssh = db.execute(
            "SELECT COUNT(*) FROM events WHERE service='SSH'"
        ).fetchone()[0]
        http = db.execute(
            "SELECT COUNT(*) FROM events WHERE service='HTTP'"
        ).fetchone()[0]

    table_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(r["timestamp"])),
            html.escape(str(r["source_ip"])),
            html.escape(str(r["service"])),
            html.escape(str(r["method"] or "-")),
            html.escape(str(r["path"] or "-")),
            html.escape(str(r["details"] or "-"))
        ) for r in rows
    )

    if not table_rows:
        table_rows = '<tr><td colspan="6">No events yet.</td></tr>'

    return """<!doctype html><html><head><meta charset="utf-8">
    <meta http-equiv="refresh" content="5">
    <title>Simple Honeypot Dashboard</title>
    <style>
    body{font-family:Arial,sans-serif;background:#101827;color:#e8eef8;margin:0;padding:24px}
    h1{margin-bottom:4px}.muted{color:#9fb0c7}
    .cards{display:flex;gap:14px;flex-wrap:wrap;margin:22px 0}
    .card{background:#1c2a3d;padding:18px 22px;border-radius:12px;min-width:140px}
    .num{font-size:30px;font-weight:bold;color:#69d6c5}
    table{width:100%;border-collapse:collapse;background:#1c2a3d}
    th,td{text-align:left;padding:11px;border-bottom:1px solid #34445b;
    font-size:13px;overflow-wrap:anywhere}
    th{background:#263951}a{color:#69d6c5}
    </style></head><body>
    <h1>🛡 Simple Honeypot Dashboard</h1>
    <div class="muted">Fake SSH / HTTP activity monitor · Auto-refreshes every 5 seconds</div>
    <div class="cards">
    <div class="card">Total events<div class="num">""" + str(total) + """</div></div>
    <div class="card">Unique source IPs<div class="num">""" + str(unique) + """</div></div>
    <div class="card">SSH events<div class="num">""" + str(ssh) + """</div></div>
    <div class="card">HTTP events<div class="num">""" + str(http) + """</div></div>
    </div>
    <p><a href="/export">Download CSV logs</a> · <a href="/">Refresh dashboard</a></p>
    <h2>Recent connection activity</h2>
    <table><thead><tr><th>Timestamp</th><th>Source IP</th>
    <th>Service</th><th>Method</th><th>Path</th><th>Details</th></tr></thead>
    <tbody>""" + table_rows + """</tbody></table>
    <p class="muted">Academic demonstration. Public dashboard; fake SSH and HTTP listeners are local-only.</p>
    </body></html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/export":
            rows = query_events(100000)
            from io import StringIO

            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "id", "timestamp", "source_ip", "service",
                    "method", "path", "details"
                ]
            )
            writer.writeheader()
            writer.writerows(rows)

            data = output.getvalue().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header(
                "Content-Disposition",
                'attachment; filename="honeypot_logs.csv"'
            )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        page = dashboard_html().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def log_message(self, fmt, *args):
        return


def main():
    init_db()

    print("\nSIMPLE HONEYPOT STARTED")
    print(f"Dashboard listening on {DASHBOARD_HOST}:{DASHBOARD_PORT}")
    print(f"Fake HTTP: http://{HOST}:{HTTP_PORT}")
    print(f"Fake SSH: {HOST}:{SSH_PORT}")
    print("Press Ctrl+C to stop.\n")

    threading.Thread(target=ssh_server, daemon=True).start()

    httpd = ThreadingHTTPServer((HOST, HTTP_PORT), FakeHTTPHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    # Render's public dashboard listener
    dashboard = ThreadingHTTPServer(
        (DASHBOARD_HOST, DASHBOARD_PORT),
        DashboardHandler
    )

    try:
        dashboard.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping honeypot...")
    finally:
        httpd.shutdown()
        dashboard.shutdown()


if __name__ == "__main__":
    main()
