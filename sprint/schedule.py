"""Place thesis blocks into free time before a deadline.

Rules:
  * Blocks go in the order written, into your working windows.
  * After every few blocks comes a buffer block. Tangents you parked during
    the work get explored there, and only there. That keeps the spiralling
    small without banning it: some of the best evidence turns up in a tangent.
  * Anything busy on your calendar (from Calendly, if connected) is skipped.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Tuple
from zoneinfo import ZoneInfo

import yaml


@dataclass
class Block:
    title: str
    minutes: int
    done_when: str
    kind: str = "work"  # work | buffer


@dataclass
class Slot:
    block: Block
    start: datetime
    end: datetime


@dataclass
class Plan:
    thesis: str
    tz: ZoneInfo
    start: date
    deadline: date
    windows: dict  # "mon".."sun" -> list of (time, time)
    buffer_share: float
    buffer_every: int
    blocks: List[Block]


DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _t(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def load_plan(path) -> Plan:
    raw = yaml.safe_load(open(path, encoding="utf-8"))
    windows = {d: [] for d in DAYS}
    for days, spans in raw["windows"].items():
        keys = DAYS[:5] if days == "weekdays" else DAYS[5:] if days == "weekends" else [d.strip() for d in days.split(",")]
        for k in keys:
            windows[k] = [(_t(a), _t(b)) for a, b in (s.split("-") for s in spans)]
    return Plan(
        thesis=raw["thesis"],
        tz=ZoneInfo(raw.get("timezone", "Asia/Kolkata")),
        start=date.fromisoformat(str(raw["start"])),
        deadline=date.fromisoformat(str(raw["deadline"])),
        windows=windows,
        buffer_share=float(raw.get("buffer_share", 0.2)),
        buffer_every=int(raw.get("buffer_every", 3)),
        blocks=[Block(b["title"], int(b["minutes"]), b.get("done_when", "")) for b in raw["blocks"]],
    )


def with_buffers(plan: Plan) -> List[Block]:
    out, since, spent = [], 0, 0
    for b in plan.blocks:
        out.append(b)
        since += 1
        spent += b.minutes
        if since == plan.buffer_every:
            out.append(_buffer(spent, plan.buffer_share))
            since, spent = 0, 0
    if spent:
        out.append(_buffer(spent, plan.buffer_share))
    return out


def _buffer(minutes: int, share: float) -> Block:
    m = max(15, int(round(minutes * share / 15.0)) * 15)
    return Block("Buffer: parked tangents", m, "Parking lot reviewed; anything useful moved into the draft", "buffer")


def free_spans(plan: Plan, busy: List[Tuple[datetime, datetime]]):
    day = plan.start
    while day <= plan.deadline:
        for a, b in plan.windows[DAYS[day.weekday()]]:
            spans = [(datetime.combine(day, a, plan.tz), datetime.combine(day, b, plan.tz))]
            for bs, be in busy:
                nxt = []
                for s, e in spans:
                    if be <= s or bs >= e:
                        nxt.append((s, e))
                        continue
                    if s < bs:
                        nxt.append((s, bs))
                    if be < e:
                        nxt.append((be, e))
                spans = nxt
            yield from spans
        day += timedelta(days=1)


def schedule(plan: Plan, busy: Optional[List[Tuple[datetime, datetime]]] = None):
    """Returns (placed slots, blocks that did not fit before the deadline)."""
    queue = with_buffers(plan)
    placed: List[Slot] = []
    spans = free_spans(plan, busy or [])
    cur = None
    for block in queue:
        need = timedelta(minutes=block.minutes)
        while True:
            if cur is None or cur[1] - cur[0] < need:
                cur = next(spans, None)
                if cur is None:
                    return placed, queue[queue.index(block):]
                continue
            placed.append(Slot(block, cur[0], cur[0] + need))
            cur = (cur[0] + need + timedelta(minutes=10), cur[1])  # 10-minute break between blocks
            break
    return placed, []
