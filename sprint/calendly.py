"""The two Calendly calls this repo uses.

busy_times():  what is already booked, so thesis blocks go around it
one_time_link(): a booking link that works once, for one founder
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

import requests

API = "https://api.calendly.com"


def _headers() -> dict:
    token = os.environ.get("CALENDLY_TOKEN")
    if not token:
        raise RuntimeError("CALENDLY_TOKEN is missing. Add a personal access token to .env (see .env.example).")
    return {"Authorization": f"Bearer {token}"}


def me() -> dict:
    r = requests.get(f"{API}/users/me", headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()["resource"]


def busy_times(start: datetime, end: datetime) -> List[Tuple[datetime, datetime]]:
    """Calendly allows up to 7 days per call, so longer ranges are fetched week by week."""
    user = me()["uri"]
    out, cur = [], start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    while cur < end:
        stop = min(cur + timedelta(days=7), end)
        r = requests.get(
            f"{API}/user_busy_times",
            headers=_headers(),
            params={"user": user, "start_time": cur.isoformat().replace("+00:00", "Z"),
                    "end_time": stop.isoformat().replace("+00:00", "Z")},
            timeout=30,
        )
        r.raise_for_status()
        for item in r.json().get("collection", []):
            out.append((datetime.fromisoformat(item["start_time"].replace("Z", "+00:00")),
                        datetime.fromisoformat(item["end_time"].replace("Z", "+00:00"))))
        cur = stop
    return out


def event_type_uri(name: str) -> str:
    r = requests.get(f"{API}/event_types", headers=_headers(), params={"user": me()["uri"]}, timeout=30)
    r.raise_for_status()
    for et in r.json().get("collection", []):
        if et["name"].lower() == name.lower():
            return et["uri"]
    raise RuntimeError(f"No Calendly event type called '{name}'. Create it in Calendly first.")


def one_time_link(event_type: str) -> str:
    r = requests.post(
        f"{API}/scheduling_links",
        headers=_headers(),
        json={"max_event_count": 1, "owner": event_type, "owner_type": "EventType"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["resource"]["booking_url"]
