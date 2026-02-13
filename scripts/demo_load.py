"""Generate and post synthetic robotic-surgery telemetry events.

Usage:
  python scripts/demo_load.py --count 100
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timezone

import requests


def make_event(i: int) -> dict:
    step = random.choice(["incision", "dissection", "suturing", "closure"])
    return {
        "event_id": f"evt-{i:05d}",
        "patient_id": f"pat-{(i % 7) + 1}",
        "procedure_id": f"proc-{(i % 3) + 1}",
        "robot_arm": random.choice(["arm_1", "arm_2", "arm_3", "camera"]),
        "step": step,
        "force_newtons": round(random.uniform(6, 45), 2),
        "velocity_mm_s": round(random.uniform(5, 30), 2),
        "latency_ms": random.randint(12, 180),
        "error_code": random.choice([None, None, None, "HAPTIC_DRIFT", "CAM_OCCLUSION"]),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attributes": {"or_room": random.choice(["OR-1", "OR-2", "OR-3"])},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--ingest-url", default="http://localhost:8080/events")
    parser.add_argument("--index-url", default="http://localhost:8081/index")
    args = parser.parse_args()

    for i in range(args.count):
        event = make_event(i)
        ingest = requests.post(args.ingest_url, json=event, timeout=5)
        index = requests.post(args.index_url, json=event, timeout=5)
        ingest.raise_for_status()
        index.raise_for_status()

    print(f"Posted {args.count} events to ingest and index services.")


if __name__ == "__main__":
    main()
