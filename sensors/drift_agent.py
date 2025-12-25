# sensors/drift_agent.py
"""
Simulate configuration drift detection by writing config_drift events.
This agent can be used to emulate an unexpected config change or its remediation.
"""
import time
import argparse
from utils.db_utils import insert_event


# ---------------- EXISTING LOGIC (UNCHANGED) ----------------

def simulate_change(details="firewall_rule_added"):
    insert_event("config_drift", details=details)
    print("config_drift event inserted:", details)


# ---------------- NEW LOGIC (ADDED, NOT BREAKING) ----------------

def simulate_remediation(details="firewall_rule_reverted"):
    insert_event("config_revert", details=details)
    print("config_revert event inserted:", details)


# ---------------- MAIN ENTRY ----------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", default="firewall_rule_added")
    parser.add_argument("--revert", action="store_true")
    args = parser.parse_args()

    if args.revert:
        simulate_remediation(args.details)
    else:
        simulate_change(args.details)
