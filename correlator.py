# correlator.py
"""
Scoring and correlation logic. Uses a small deterministic rule-based scoring:
- honeypot events are high-weight
- missing-heartbeats (absence signals) are high-weight
- configuration drift events have medium weight
Outputs: dict containing threat_score (0-100), alerts (list), breakdown
"""

from datetime import datetime, timedelta
import time

from utils.db_utils import fetch_events_since, fetch_latest_event
from config import LOOKBACK_SECONDS, HEARTBEAT_THRESHOLD, HEARTBEAT_MISSED_CYCLES

# weights
WEIGHT_HONEYPOT = 50
WEIGHT_ABSENCE = 30
WEIGHT_DRIFT = 20

def compute_threat():
    """
    returns: {
        'threat_score': int,
        'alerts': [str],
        'breakdown': {...}
    }
    """
    now_ts = int(datetime.utcnow().timestamp())
    since_ts = now_ts - LOOKBACK_SECONDS
    events = fetch_events_since(since_ts)

    alerts = []
    honeypot_count = 0
    drift_count = 0
    absence_count = 0

    # count events by type
    for _id, etype, subtype, details, ts in events:
        if etype == "honeypot_access":
            honeypot_count += 1
            alerts.append(f"Honeypot accessed: {details or 'unknown'}")
        elif etype == "config_drift":
            drift_count += 1
            alerts.append(f"Config drift: {details or subtype or 'change detected'}")
        elif etype == "expected_event_missing":
            absence_count += 1
            alerts.append(f"Missing expected event: {details or subtype or 'unknown'}")

    # Detect heartbeat absence from heartbeat events
    # Approach: check latest heartbeat timestamp and see if it's too old
    hb_row = fetch_latest_event("heartbeat")
    heartbeat_missing = False
    if hb_row:
        hb_ts = hb_row[4]
        # if now - hb_ts > HEARTBEAT_THRESHOLD * HEARTBEAT_MISSED_CYCLES => missing
        if (now_ts - hb_ts) > (HEARTBEAT_THRESHOLD * HEARTBEAT_MISSED_CYCLES):
            heartbeat_missing = True
            absence_count += 1
            alerts.append("Heartbeat missing or delayed (possible agent stopped)")
    else:
        # never got a heartbeat in history window
        heartbeat_missing = True
        absence_count += 1
        alerts.append("No heartbeat recorded (agent silent)")

    # Construct a simple scoring:
    score = 0
    # If there were honeypot events recently, high weight
    if honeypot_count > 0:
        score += WEIGHT_HONEYPOT * min(honeypot_count, 3)  # cap contribution
    # absence contribution scaled
    score += WEIGHT_ABSENCE * min(absence_count, 3)
    # drift contribution scaled
    score += WEIGHT_DRIFT * min(drift_count, 5)

    # normalize to 0-100
    score = max(0, int(score))
    if score > 100:
        score = 100

    # Add friendly heuristics
    if heartbeat_missing and honeypot_count > 0:
        # attacker attacked and then killed agent -> raise confidence
        alerts.append("High confidence: honeypot touch + heartbeat missing")
    elif honeypot_count > 0 and drift_count > 0:
        alerts.append("Honeypot + config drift — suspicious activity")

    # dedupe alerts
    unique_alerts = []
    for a in alerts:
        if a not in unique_alerts:
            unique_alerts.append(a)

    result = {
        "threat_score": score,
        "alerts": unique_alerts,
        "counts": {
            "honeypot": honeypot_count,
            "drift": drift_count,
            "absence": absence_count,
            "heartbeat_missing": heartbeat_missing
        },
        "generated_at": now_ts
    }
    return result
