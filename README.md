# Zero-Log Attack Surface Detector (ZLASD) — Prototype

## Overview
ZLASD detects stealthy attacks that remove or tamper logs by using:
- Honeypot / canary events
- Absence-of-expected-events (heartbeats, scheduled tasks)
- Configuration drift events

It correlates these signals and shows a professional web dashboard.

## Requirements
- Python 3.10 (recommended)
- pip

## Setup (Linux/macOS)
```bash
# create venv with Python 3.10
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

.venv\Scripts\activate
python app.py
.venv\Scripts\activate
python -m sensors.heartbeat_agent --interval 30
.venv\Scripts\activate
python -m sensors.honeypot_agent --interval 30
.venv\Scripts\activate
python -m sensors.drift_agent --details "firewall_rule_added simulated"

tasklist | findstr python
taskkill /F /PID 17316