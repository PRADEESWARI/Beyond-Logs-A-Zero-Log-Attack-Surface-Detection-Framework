# sensors/honeypot_agent.py
"""
Simple honeypot simulator.

Modes:
1. Default (no args):
   - Monitors a real honeypot file for access/modification
2. --once:
   - Inserts a single honeypot_access event (manual demo)
3. --loop:
   - Periodically creates honeypot_access events (simulation demo)
"""

import time
import argparse
import os
from utils.db_utils import insert_event

# 🔐 Real honeypot file path
HONEYPOT_FILE = "honeypot/honey_file.txt"


# ---------------- EXISTING LOGIC (UNCHANGED) ----------------

def run_once():
    insert_event("honeypot_access", details="canary_file_read")
    print("honeypot_access event inserted")


def run_loop(interval=60):
    print("honeypot loop started, interval:", interval)
    try:
        while True:
            run_once()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("honeypot loop stopped")


# ---------------- NEW REAL HONEYPOT LOGIC ----------------

def monitor_honeypot():
    if not os.path.exists(HONEYPOT_FILE):
        print(f"[ERROR] Honeypot file not found: {HONEYPOT_FILE}")
        print("Create it using: honeypot/honey_file.txt")
        return

    print("[HONEYPOT] Real honeypot monitoring started...")
    last_mtime = os.path.getmtime(HONEYPOT_FILE)

    try:
        while True:
            time.sleep(1)
            current_mtime = os.path.getmtime(HONEYPOT_FILE)

            if current_mtime != last_mtime:
                insert_event(
                    "honeypot_access",
                    details="honeypot file accessed or modified"
                )
                print("[ALERT] Honeypot file accessed!")
                last_mtime = current_mtime
    except KeyboardInterrupt:
        print("Honeypot monitoring stopped.")


# ---------------- MAIN ENTRY ----------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args()

    if args.loop:
        run_loop(args.interval)
    elif args.once:
        run_once()
    else:
        monitor_honeypot()
