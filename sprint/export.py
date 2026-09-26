"""Write the schedule as a calendar file (.ics) and a plain checklist (.md).

The .ics file imports into Google Calendar, Outlook or Apple Calendar.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from .schedule import Plan, Slot


def _utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> List[str]:
    """Calendar files want lines of 75 bytes at most; longer ones continue after a space."""
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode("utf-8")) > (75 if not out else 74):
            out.append(cur)
            cur = ""
        cur += ch
    out.append(cur)
    return [out[0]] + [" " + part for part in out[1:]]


def _hm(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h}h {m}m" if h and m else f"{h}h" if h else f"{m}m"


def write_ics(plan: Plan, slots: List[Slot], path: Path) -> None:
    now = _utc(datetime.now(timezone.utc))
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//thesis-sprints//EN", "CALSCALE:GREGORIAN"]
    for s in slots:
        uid = hashlib.sha1(f"{plan.thesis}|{s.block.title}|{s.start.isoformat()}".encode()).hexdigest()
        desc = f"Done when: {s.block.done_when}"
        if s.block.kind == "work":
            desc += "\nNew idea that is off this block? Write it in parking-lot.md and keep going."
        lines += [
            "BEGIN:VEVENT", f"UID:{uid}@thesis-sprint", f"DTSTAMP:{now}",
            f"DTSTART:{_utc(s.start)}", f"DTEND:{_utc(s.end)}",
            f"SUMMARY:{_esc(plan.thesis + ': ' + s.block.title)}",
            f"DESCRIPTION:{_esc(desc)}", "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    folded = [part for line in lines for part in _fold(line)]
    path.write_text("\r\n".join(folded) + "\r\n", encoding="utf-8", newline="")


def write_checklist(plan: Plan, slots: List[Slot], unplaced, path: Path) -> None:
    work = sum(s.block.minutes for s in slots if s.block.kind == "work")
    buf = sum(s.block.minutes for s in slots if s.block.kind == "buffer")
    out = [f"# {plan.thesis}", "",
           f"{len(slots)} blocks from {plan.start} to {plan.deadline}. "
           f"{_hm(work)} of planned work, {_hm(buf)} of buffer for tangents.",
           "", "Ideas that come up mid-block go in `parking-lot.md` and wait for the next buffer block."]
    day = None
    for s in slots:
        d = s.start.strftime("%a %d %b")
        if d != day:
            out += ["", f"## {d}", ""]
            day = d
        out.append(f"- [ ] {s.start:%H:%M}-{s.end:%H:%M} **{s.block.title}**. Done when: {s.block.done_when}")
    if unplaced:
        out += ["", "## Did not fit before the deadline", ""]
        out += [f"- {b.title} ({b.minutes} min)" for b in unplaced]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
