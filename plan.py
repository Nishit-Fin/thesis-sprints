"""Split a thesis into timed blocks and put them on your calendar.

    python plan.py examples/quantum-sprint.yaml              # uses only your working windows
    python plan.py examples/quantum-sprint.yaml --calendly   # also skips anything booked in Calendly

Writes <plan>.ics (import into Google Calendar or Outlook) and <plan>.md (checklist).
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, time
from pathlib import Path

from dotenv import load_dotenv

from sprint.export import write_checklist, write_ics
from sprint.schedule import load_plan, schedule


def main() -> int:
    load_dotenv()
    ap = argparse.ArgumentParser(description="Turn a thesis plan into calendar blocks.")
    ap.add_argument("plan", type=Path)
    ap.add_argument("--calendly", action="store_true", help="avoid times already booked in Calendly")
    args = ap.parse_args()

    plan = load_plan(args.plan)
    busy = []
    if args.calendly:
        from sprint.calendly import busy_times
        busy = busy_times(datetime.combine(plan.start, time(0, 0), plan.tz),
                          datetime.combine(plan.deadline, time(23, 59), plan.tz))
        print(f"Calendly: {len(busy)} busy slots skipped")

    slots, unplaced = schedule(plan, busy)
    ics, md = args.plan.with_suffix(".ics"), args.plan.with_suffix(".md")
    write_ics(plan, slots, ics)
    write_checklist(plan, slots, unplaced, md)
    print(f"{len(slots)} blocks placed. Wrote {ics} and {md}.")
    if unplaced:
        print(f"{len(unplaced)} blocks did not fit before {plan.deadline}. Cut scope or add time.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
