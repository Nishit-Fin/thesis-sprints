---
name: thesis-sprint
description: Split an investment thesis into timed blocks with a clear finish line each, put them on the calendar, and keep a small, planned buffer for tangents. Use when starting a thesis or when research is drifting.
---

# Thesis sprint

Thesis work drifts. One interesting link leads to ten more, and two evenings
later the market size still is not done. This skill does not ban the drift.
It gives it a place: tangents get written down and explored in buffer blocks,
not in the middle of the work.

## Steps

1. **Ask before planning.** Deadline? Which evenings and weekend hours are free?
   What does "done" look like for the whole thesis (a memo, a deck, a form answer)?
2. **Split the work** into blocks of 45 to 150 minutes. Every block gets a
   "done when" line that someone else could check. "Research the market" is
   not a block. "Buyers x price for QKD, every input sourced" is.
3. **Add buffers.** 20% extra time, as one buffer block after every 3 work
   blocks. Only parked tangents are explored there.
4. **Find free time.**
   - Calendly connected: read busy times first and plan around them.
   - Google Calendar connected: create the blocks there directly, with the
     "done when" line in the event description.
   - Neither: run `python plan.py <plan>.yaml` and import the `.ics` file.
5. **During the work,** any idea off the current block goes into
   `parking-lot.md` with one line on why it might matter. Then back to the block.
6. **End of each block,** check the "done when" line. Not done? Move the rest
   to the next buffer, not into tomorrow's block.
7. **Weekly,** a scheduled task reads the parking lot and asks which items earned
   a place in the thesis.

## Rules

- Never schedule over something already booked.
- If the blocks do not fit before the deadline, say so and ask what to cut.
  Do not squeeze blocks shorter.
- Plain words. No em dashes.
