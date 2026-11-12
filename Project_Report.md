# SIMPLE HONEYPOT
## Fake SSH/HTTP Service with Connection Logging and Attacker IP Dashboard

### Abstract
A honeypot is a decoy system used in cybersecurity to observe connection attempts and suspicious activity. This project implements a lightweight academic honeypot with a fake SSH banner listener and a fake HTTP service. It records connection metadata such as timestamp, source IP address, service type, HTTP method and requested path. A browser-based dashboard displays event statistics and recent activity. SQLite is used for local log storage, and logs can be exported as a CSV file.

### Objectives
1. Build a fake SSH listener to observe TCP connection attempts.
2. Build a fake HTTP service to record incoming HTTP requests.
3. Store event details with timestamps and source IP addresses.
4. Display collected events and summary statistics on a dashboard.
5. Export collected logs for further analysis.

### Software and hardware requirements
- Windows 10/11 computer
- Python 3.9+
- VS Code (optional)
- Web browser
- SQLite (included with Python)

### Modules
**1. Fake SSH module:** Listens on TCP port 2222, sends a demonstration SSH banner and records connection attempts. It does not authenticate users or collect passwords.

**2. Fake HTTP module:** Listens on port 8080 and records request method, path, source IP and limited User-Agent information.

**3. Logging module:** Stores events in an SQLite database with timestamps.

**4. Dashboard module:** Runs on port 5000 and shows total events, unique source IPs, SSH events, HTTP events and recent logs.

**5. CSV export module:** Exports the recorded events for reporting and analysis.

### System workflow
Client/test tool → Fake SSH or HTTP service → Event logger → SQLite database → Dashboard / CSV export.

### Expected output
When a test connection is made, the event is stored in the database. The dashboard displays the source IP, timestamp and service details. For local testing, the source IP is expected to be 127.0.0.1.

### Result
The prototype demonstrates the basic working principle of a honeypot by creating decoy network services, recording connection metadata and presenting the collected information through a local dashboard.

### Conclusion
The Simple Honeypot project provides a basic demonstration of defensive cybersecurity monitoring. It helps students understand how decoy services can be used to observe network activity and maintain event logs. Future improvements could include geolocation enrichment, alert notifications, charts and deployment across an isolated virtual network.

### Ethical and safety note
This implementation is intended for an authorized academic lab. It binds to localhost by default, does not collect credentials and must not be exposed to the public internet or used on networks without permission.
