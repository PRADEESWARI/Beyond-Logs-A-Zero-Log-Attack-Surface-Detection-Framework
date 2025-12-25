# config.py
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "events.db")
LOG_PATH = os.path.join(BASE_DIR, "logs", "app.log")

# Correlation windows (seconds)
LOOKBACK_SECONDS = 180            # how far back correlator looks for events (3 minutes)
HEARTBEAT_THRESHOLD = 60         # expected heartbeat interval (seconds)
HEARTBEAT_MISSED_CYCLES = 2      # if no heartbeat for (threshold * cycles) => missing
