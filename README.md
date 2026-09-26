# Thesis Sprints

Thesis work drifts. One good link leads to ten more, and two evenings later the market size is
still not done. This repo splits a thesis into timed blocks, each with a finish line someone else
could check, and puts them on my calendar around what is already booked.

It reduces the drift without banning it. Ideas that come up mid-block go into a
[parking lot](parking-lot.md) and get explored in buffer blocks (20% extra time), because a
tangent sometimes turns up the best evidence.

## Result

My next pass on the quantum thesis, closing the questions the first version left open:
[the plan](plans/quantum-second-pass.yaml) became [11 calendar blocks over six weekday mornings](plans/quantum-second-pass.md)
(8h 45m of work, 2h of buffer), plus a [calendar file](plans/quantum-second-pass.ics) that imports into
Google Calendar or Outlook.

## Which tool does what

| Job | Tool | Why this one |
|---|---|---|
| Split the thesis, keep the parking lot | Claude, with the [thesis-sprint skill](skills/thesis-sprint/SKILL.md) | Turns "research the market" into blocks with a checkable finish line |
| Put the blocks on my calendar | Google Calendar (Claude connector), or the `.ics` file | Calendly books meetings with other people. It cannot block my own time |
| Keep blocks off booked calls | Calendly busy times | Blocks go around founder calls already booked |
| Founder calls | Calendly one-time links, with the [founder-outreach skill](skills/founder-outreach/SKILL.md) | Each founder gets their own link, so every booking traces back to one email |
| Outreach emails | Gmail (Claude connector), drafts only | I read and send every email myself |
| LinkedIn posts | My [LinkedIn skills fork](https://github.com/Nishit-Fin/linkedin-skills-vc), which schedules through Publora | Calendly and Gmail cannot post to LinkedIn |

## Run it

```
pip install -r requirements.txt
python plan.py plans/quantum-second-pass.yaml              # working windows only
python plan.py plans/quantum-second-pass.yaml --calendly   # also skips Calendly bookings (CALENDLY_TOKEN in .env)
python outreach.py examples/founders.yaml --no-links       # one email draft per founder
python -m pytest -q                                        # offline checks
```

If the blocks do not fit before the deadline, the planner says what is left over instead of
squeezing blocks shorter.

## Code

```
plan.py              plan.yaml -> calendar file (.ics) + checklist (.md)
outreach.py          founders.yaml -> email drafts, each with its own Calendly link
sprint/schedule.py   places work and buffer blocks into free time
sprint/calendly.py   Calendly busy times and one-time booking links
sprint/export.py     calendar file and checklist writers
```
