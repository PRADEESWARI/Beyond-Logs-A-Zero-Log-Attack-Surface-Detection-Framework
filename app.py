# app.py
from flask import Flask, jsonify, render_template, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import os

from config import LOG_PATH, DB_PATH
from utils.db_utils import ensure_db, insert_event, fetch_events_since
from correlator import compute_threat

# Setup logging & folders
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')
log = logging.getLogger("zlasd")

app = Flask(__name__, static_folder="static", template_folder="templates")

# in-memory latest status to avoid computing each API call
LATEST_STATUS = {
    "threat_score": 0,
    "alerts": [],
    "counts": {},
    "generated_at": int(datetime.utcnow().timestamp())
}

def scheduled_correlator():
    try:
        res = compute_threat()
        LATEST_STATUS.update(res)
        log.info(f"Computed threat score {res['threat_score']} alerts={len(res['alerts'])}")
    except Exception as e:
        log.exception("Correlator error: %s", e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def api_status():
    # serve latest status and also recent events for UI
    since_ts = int(datetime.utcnow().timestamp()) - 600
    events = fetch_events_since(since_ts)
    # map events to nice objects
    ev = [{
        "id": r[0],
        "type": r[1],
        "subtype": r[2],
        "details": r[3],
        "ts": r[4]
    } for r in events]
    payload = {
        "status": LATEST_STATUS,
        "recent_events": ev
    }
    return jsonify(payload)

# small helper: produce a test event from browser (for demo)
@app.route("/api/trigger/<kind>")
def api_trigger(kind):
    # allowed kinds: honeypot, drift, missing, heartbeat
    if kind == "honeypot":
        insert_event("honeypot_access", details="web-triggered-demo")
    elif kind == "drift":
        insert_event("config_drift", details="web-triggered-change")
    elif kind == "missing":
        insert_event("expected_event_missing", details="web-triggered-missing-backup")
    elif kind == "heartbeat":
        insert_event("heartbeat", details="web-triggered-heartbeat")
    else:
        return jsonify({"ok": False, "error": "unknown kind"})
    return jsonify({"ok": True})

if __name__ == "__main__":
    # ensure DB exists
    ensure_db()
    # start scheduled correlator
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_correlator, 'interval', seconds=10)
    scheduler.start()
    try:
        # compute once on startup
        scheduled_correlator()
        # run flask
        app.run(host="0.0.0.0", port=5000, debug=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
