# SIMPLE HONEYPOT – Fake SSH/HTTP Monitoring

## Project overview
This academic cybersecurity demonstration runs two deliberately fake services:
- Fake SSH banner listener on TCP port **2222**. It records connection attempts and sends a banner. It is not a real SSH server and does not accept logins.
- Fake HTTP service on port **8080**. It records HTTP requests, source IP, method, path and User-Agent.
- Local dashboard on port **5000**. It displays total events, unique source IPs, SSH/HTTP counts and recent events. It refreshes every five seconds and exports CSV logs.

Events are stored in `honeypot_logs.db` (SQLite).

## Requirements
- Windows 10/11
- Python 3.9 or newer
- VS Code (optional)

No third-party Python packages are required.

## Run on Windows
1. Extract the ZIP file.
2. Open the extracted `Simple_Honeypot_Project` folder.
3. Double-click `run.bat`.
4. A terminal window should show that the services started.
5. Open **http://127.0.0.1:5000** in your browser.

If Windows asks about firewall access, keep it blocked for public networks. The project defaults to localhost only.

## Test the services
Keep the project running. Open a second Command Prompt.

Test HTTP:
```bat
curl http://127.0.0.1:8080/test-page
```

Test SSH banner:
```bat
python -c "import socket; s=socket.create_connection(('127.0.0.1',2222)); print(s.recv(200).decode()); s.close()"
```

Refresh the dashboard at http://127.0.0.1:5000. You should see events from `127.0.0.1`. Click **Download CSV logs** to export them.

## Project architecture
1. Client/test tool connects to fake SSH or HTTP listener.
2. Listener reads connection metadata/request details.
3. `log_event()` stores the event in SQLite with timestamp and source IP.
4. Dashboard queries SQLite and displays recent events and summary counts.
5. CSV export allows analysis in Excel.

## Important limitation
This is a safe, lightweight honeypot simulation for a college demonstration. The SSH component is a fake banner listener, not a full SSH protocol implementation. It does not collect passwords or credentials. By default, all services listen only on `127.0.0.1`, so tests from the same computer are recorded as `127.0.0.1`. Do not expose it to the public internet or use it on networks without permission.

## Troubleshooting
- **Python not found:** Install Python from https://www.python.org/downloads/ and tick “Add Python to PATH”.
- **Port already in use:** Close the other program using port 2222, 8080 or 5000, or change the port values at the top of `honeypot.py`.
- **Dashboard does not open:** Confirm the terminal is still running and visit `http://127.0.0.1:5000`.
- **No events:** Run the HTTP and SSH test commands above, then refresh the dashboard.

## Viva / presentation points
**What is a honeypot?** A decoy system designed to attract and observe suspicious or unauthorized activity.

**Why use it?** To study connection attempts, identify source IP addresses, understand attacker behaviour and improve defensive monitoring.

**What does this project capture?** Timestamp, source IP, service type, HTTP method/path and limited request metadata.

**Where are logs stored?** In a local SQLite database named `honeypot_logs.db`.

**What is the dashboard port?** TCP port 5000.

**What are the service ports?** Fake SSH uses 2222 and fake HTTP uses 8080.

**What is the limitation?** The SSH service imitates an SSH banner only; it is not a full SSH server. The project is intended for a controlled academic lab.
