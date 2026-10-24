#!/usr/bin/env python3
"""
Find the UC... channel id for one or more YouTube channels.

Accepts handles (@name), channel URLs, or bare UC... ids and prints the
resolved id for each. Useful for filling in channels.txt.

Usage:
    python tools/find_channel_id.py @veritasium
    python tools/find_channel_id.py @veritasium @mkbhd https://youtube.com/@Fireship
"""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request

USER_AGENT = "Mozilla/5.0 (compatible; yt-telegram-notifier/1.0)"
CHANNEL_ID_RE = re.compile(r'"channelId":"(UC[\w-]{22})"')
EXTERNAL_ID_RE = re.compile(r'"externalId":"(UC[\w-]{22})"')
BARE_ID_RE = re.compile(r"^UC[\w-]{22}$")

def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def resolve(spec: str) -> str | None:
    spec = spec.strip()
    if BARE_ID_RE.match(spec):
        return spec

    if spec.startswith("@"):
        url = f"https://www.youtube.com/{spec}"
    elif "youtube.com" in spec or "youtu.be" in spec:
        url = spec
    else:
        return None

    try:
        page = fetch(url).decode("utf-8", "replace")
    except Exception as e:
        print(f"[error] {spec}: {e}", file=sys.stderr)
        return None

    for rx in (CHANNEL_ID_RE, EXTERNAL_ID_RE):
        m = rx.search(page)
        if m:
            return m.group(1)
    return None

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    exit_code = 0
    for spec in argv[1:]:
        cid = resolve(spec)
        if cid:
            print(f"{spec}  ->  {cid}")
        else:
            print(f"{spec}  ->  ??? (could not resolve)", file=sys.stderr)
            exit_code = 1
    return exit_code

if __name__ == "__main__":
    sys.exit(main(sys.argv))
