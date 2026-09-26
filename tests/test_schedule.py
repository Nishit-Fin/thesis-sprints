"""Offline checks for the planner: python -m pytest -q"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sprint.schedule import load_plan, schedule  # noqa: E402

PLAN = Path(__file__).resolve().parents[1] / "plans" / "quantum-second-pass.yaml"


def test_every_block_fits_in_the_working_window():
    plan = load_plan(PLAN)
    slots, unplaced = schedule(plan)
    assert not unplaced
    for s in slots:
        assert s.start.weekday() < 5  # weekdays only in this plan
        assert (s.start.hour, s.start.minute) >= (10, 0)
        assert (s.end.hour, s.end.minute) <= (12, 30)


def test_buffer_is_about_a_fifth_of_the_work():
    plan = load_plan(PLAN)
    slots, _ = schedule(plan)
    work = sum(s.block.minutes for s in slots if s.block.kind == "work")
    buffer = sum(s.block.minutes for s in slots if s.block.kind == "buffer")
    assert 0.15 <= buffer / work <= 0.3


def test_busy_time_is_skipped():
    plan = load_plan(PLAN)
    call = (datetime(2026, 9, 28, 10, 0, tzinfo=plan.tz), datetime(2026, 9, 28, 11, 0, tzinfo=plan.tz))
    slots, _ = schedule(plan, [call])
    assert all(s.end <= call[0] or s.start >= call[1] for s in slots)


def test_too_little_time_is_reported_not_squeezed():
    plan = load_plan(PLAN)
    plan.deadline = plan.start  # one morning for the whole plan
    slots, unplaced = schedule(plan)
    assert unplaced
    assert all(s.block.minutes == (s.end - s.start).seconds // 60 for s in slots)
