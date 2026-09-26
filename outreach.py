"""Draft founder emails, each with its own one-time Calendly link.

    python outreach.py examples/founders.yaml

Writes one draft per founder to drafts/. Nothing is sent. I read each draft,
edit the first line so it is really about their company, then send it from
Gmail myself (or have Claude put it in Gmail as a draft).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument("founders", type=Path)
    ap.add_argument("--no-links", action="store_true", help="skip Calendly, leave a placeholder")
    args = ap.parse_args()

    cfg = yaml.safe_load(args.founders.read_text(encoding="utf-8"))
    template = cfg["template"]
    event_type = None
    if not args.no_links:
        from sprint.calendly import event_type_uri, one_time_link
        event_type = event_type_uri(cfg["calendly_event_type"])

    out = Path("drafts")  # git ignores this folder: drafts hold real names and emails
    out.mkdir(exist_ok=True)
    for f in cfg["founders"]:
        link = one_time_link(event_type) if event_type else "[booking link]"
        body = template.format(first_name=f["name"].split()[0], company=f["company"], why=f["why"],
                               link=link, sender=cfg["sender"])
        subject = cfg["subject"].format(company=f["company"])
        path = out / f"{f['company'].lower().replace(' ', '-')}.md"
        path.write_text(f"To: {f['email']}\nSubject: {subject}\n\n{body}", encoding="utf-8")
        print(f"Draft: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
