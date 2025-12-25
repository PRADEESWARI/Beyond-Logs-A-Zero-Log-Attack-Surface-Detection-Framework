# sensors/heartbeat_agent.py
"""
Simple heartbeat agent. Run on each host. It writes a heartbeat event every N seconds.
Usage:
    python sensors/heartbeat_agent.py --interval 30
"""
import time
import argparse
from utils.db_utils import insert_event

def run(interval=30):
    print("Heartbeat agent started (CTRL+C to stop). Interval:", interval)
    try:
        while True:
            insert_event("heartbeat", details="heartbeat")
            print("heartbeat event inserted")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Heartbeat agent stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()
    run(args.interval)
