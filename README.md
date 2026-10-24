# YouTube to Telegram Notifier (Free, Serverless)

Monitors any number of YouTube channels and automatically sends every new video to a Telegram chat or channel as **both a text link and an audio voice message**.

Runs entirely on **GitHub Actions** — no server, no phone required, completely free.

---

## What is inside this package?

| File | Purpose |
|---|---|
| `notify.py` | Main script: reads YouTube RSS feeds, downloads audio, sends to Telegram |
| `channels.txt` | List of channels to monitor |
| `.github/workflows/notify.yml` | GitHub Actions scheduler (runs every 15 minutes) |
| `tools/find_channel_id.py` | Helper script to resolve `@handle` or URLs to `UC...` IDs |
| `requirements.txt` | Empty — standard library only (plus `yt-dlp` installed in workflow) |

---

## Prerequisites

- A free **GitHub** account
- A **Telegram** account
- 10 minutes of your time

---

## Step 1 — Create a Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot`.
3. Choose a name (e.g. `My YT Notifier`).
4. Choose a username ending in `bot` (e.g. `my_yt_notify_bot`).
5. BotFather will give you a **token** like:
```

1234567890:AAH-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

```
Save this token in a safe place. **Never share it.**

---

## Step 2 — Get your `chat_id`

### Option A: Send to your own private chat
1. Send a message to your bot (e.g. `/start` or `hi`).
2. Open this URL in your browser (replace `<TOKEN>` with your real token):
```

https://api.telegram.org/bot<TOKEN>/getUpdates

```
3. Look for `"chat": { "id": 123456789, ... }`. That number is your `chat_id`.

### Option B: Send to a Telegram Channel
1. Add your bot to the channel and promote it to **Admin** (with permission to send messages).
2. Post a message in the channel.
3. Open the `getUpdates` URL again.
4. Look for `"chat": { "id": -1001234567890, ... }`. The ID usually starts with `-100`.

---

## Step 3 — Find YouTube `channel_id`s

Each YouTube channel has a 24-character ID starting with `UC`.

### Easiest method — use the included tool
```bash
python tools/find_channel_id.py @veritasium
# Output: @veritasium  →  UCHnyfMqiRRG1u-2MsSQLbXA
```

You can pass multiple handles at once:

```
python tools/find_channel_id.py @veritasium @mkbhd "https://youtube.com/@Fireship"
```

### Method 2 — from the channel link

Click **Share** → **Copy link** on the channel page.

- If it looks like `youtube.com/channel/UC...`, use the `UC...` part.
- If it looks like `youtube.com/@handle`, use Method 1 or 3.

### Method 3 — from page source

Open the channel page, press `Ctrl+U` (View Source), and search for `"channelId":"UC`. Copy the 24 characters after it.

---

## Step 4 — Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new).
2. Repository name: `yt-telegram-notifier`
3. Select **Public**. ⬅️ Important! Public repos have no Actions minute limit.
4. Click **Create repository**.

Now upload the files from this package:

- On the repo page, click **Add file → Upload files**.
- Drag and drop all extracted files and folders.
- Click **Commit changes**.

> If the `.github` folder was not uploaded (some browsers hide it):
> 
> - Click **Add file → Create new file**.
> - Type the path: `.github/workflows/notify.yml`
> - Paste the contents of that file and commit.

---

## Step 5 — Add Secrets

In your repository: **Settings → Secrets and variables → Actions → New repository secret**

| Name ↕▾ | Value ↕▾ |
|---|---|
| −`TELEGRAM_BOT_TOKEN` | Your BotFather token |
| −`TELEGRAM_CHAT_ID` | Your `chat_id` from Step 2 |
⚙

---

## Step 6 — Add Channels

Open `channels.txt` and list one channel per line. All three formats work:

```
UCE1P_bsD_kKh-i0HEsPpxtA
@Mr.EnglishChannel
https://youtube.com/@Fireship
```

Commit the changes.

---

## Step 7 — First Run (Seed)

1. Go to the **Actions** tab in your repository.
2. If prompted, click **I understand my workflows, go ahead and enable them**.
3. Select `youtube-to-telegram` from the left sidebar.
4. Click **Run workflow → Run workflow**.

⏳ Wait for it to finish.

**The first run intentionally sends nothing.** It only creates `state.json` and marks all current videos as "seen" so you don't get spammed with old videos.

From then on, it runs automatically every 15 minutes. Any new video will be delivered to Telegram within ~20 minutes as both a text link and a voice message.

---

## Testing

To verify your Telegram connection without waiting for a new video, go to **Actions → Run workflow** and enter `--test` in the input field.

Or locally:

```
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
python notify.py --test
```

---

## Command Line Options

```
python notify.py                # Normal run (used by Actions)
python notify.py --verbose      # More log output
python notify.py --dry-run      # Show what would be sent, don't send or save
python notify.py --test         # Send a single test message and exit
python notify.py --seed         # Rebuild state from current feeds, send nothing
```

---

## Troubleshooting

| Problem ↕▾ | Likely Cause ↕▾ | Fix ↕▾ |
|---|---|---|
| −No messages arrive | Workflow not enabled | Actions tab → Enable workflows |
| − | Wrong secrets | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| − | Bot not admin in channel | Promote the bot with send permission |
| −`400 Bad Request` | Wrong `chat_id` | Copy the exact number from `getUpdates` (include `-100`) |
| −`401 Unauthorized` | Token revoked | Get a new token from BotFather (`/token`) |
| −`403 Forbidden` | Bot blocked | Unblock the bot in Telegram |
| −`429 Too Many Requests` | Sending too fast | The script waits 1s between messages; increase cron interval |
| −Channel not found | Wrong `channel_id` | Use `tools/find_channel_id.py` |
| −Voice fails, text works | YouTube rate-limited `yt-dlp` | The text link is still sent. Retry later or reduce channels |
| −Workflow stopped after weeks | GitHub disables cron after 60 days of inactivity | The script commits `state.json` each run, which keeps it alive. If it stops, click **Run workflow** manually |
⚙

---

## FAQ

**Is it really free?**
Yes. Public repos have unlimited GitHub Actions minutes. The Telegram Bot API is free for this volume.

**How long does it take?**
Usually 5–20 minutes. GitHub cron is best-effort and may drift by a few minutes.

**Will I miss videos?**
No. YouTube RSS feeds return the last 15 videos per channel, and we check every 15 minutes. You would need >15 videos in 15 minutes to miss one.

**Do Shorts and Live streams appear?**
Yes, they are included in the same RSS feed and will be sent.

**Can I send to a group?**
Yes. Add the bot to the group, send a message, and grab the `chat.id` from `getUpdates` (usually negative).

**What if `yt-dlp` fails?**
The text message with the link is always sent first. Voice is a best-effort bonus. If YouTube blocks the download, you still get notified.

---

## License

MIT

</BDS:create_file>

<BDS:create_file fileName="notify.py">

```python
#!/usr/bin/env python3
"""
YouTube -> Telegram notifier with audio voice messages.

Reads the public RSS feed of each channel listed in channels.txt, detects new
videos, and sends them to a Telegram chat/channel as both a text message and
an audio voice message (via yt-dlp + ffmpeg).

Standard library only. Requires `yt-dlp` and `ffmpeg` on the system.
"""

from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# --- Configuration ---------------------------------------------------------

STATE_PATH = os.environ.get("STATE_PATH", "state.json")
CHANNELS_PATH = os.environ.get("CHANNELS_PATH", "channels.txt")

FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
USER_AGENT = "Mozilla/5.0 (compatible; yt-telegram-notifier/1.0)"

ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"

CHANNEL_ID_RE = re.compile(r'"channelId":"(UC[\w-]{22})"')
EXTERNAL_ID_RE = re.compile(r'"externalId":"(UC[\w-]{22})"')
BARE_ID_RE = re.compile(r"^UC[\w-]{22}$")

MAX_SEEN_PER_CHANNEL = 50
SEND_DELAY_SECONDS = 1.0
VOICE_ENABLED = os.environ.get("SEND_VOICE", "true").lower() == "true"

VERBOSE = False

# --- Helpers ---------------------------------------------------------------

def log(msg: str, *, error: bool = False) -> None:
    stream = sys.stderr if error else sys.stdout
    print(msg, file=stream, flush=True)

def vlog(msg: str) -> None:
    if VERBOSE:
        log(msg)

def fetch(url: str, *, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def read_channels(path: str) -> list[str]:
    specs: list[str] = []
    try:
        with open(path, encoding="utf-8") as f:
            for raw in f:
                line = raw.split("#", 1)[0].strip()
                if line:
                    specs.append(line)
    except FileNotFoundError:
        log(f"[fatal] channels file not found: {path}", error=True)
        sys.exit(1)
    return specs

def load_state(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "channels" not in data:
            return {"channels": {}}
        return data
    except FileNotFoundError:
        return {"channels": {}}
    except json.JSONDecodeError as e:
        log(f"[warn] state.json is corrupt ({e}); starting fresh", error=True)
        return {"channels": {}}

def save_state(path: str, state: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)

def resolve_channel_id(spec: str) -> str | None:
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
        log(f"[warn] could not resolve {spec}: {e}", error=True)
        return None

    for rx in (CHANNEL_ID_RE, EXTERNAL_ID_RE):
        m = rx.search(page)
        if m:
            return m.group(1)
    log(f"[warn] no channel id found on page for {spec}", error=True)
    return None

def parse_feed(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    entries: list[dict] = []
    for entry in root.findall(ATOM + "entry"):
        vid = entry.findtext(YT + "videoId")
        if not vid:
            continue
        title = (entry.findtext(ATOM + "title") or "").strip() or "Untitled"
        author = (entry.findtext(ATOM + "author/" + ATOM + "name") or "").strip()
        entries.append({
            "id": vid,
            "title": title,
            "author": author,
        })
    return entries

def format_message(video: dict) -> str:
    title = html.escape(video["title"])
    author = html.escape(video["author"]) if video["author"] else ""
    link = f"https://youtu.be/{video['id']}"
    lines = [f"🎬 <b>{title}</b>"]
    if author:
        lines.append(f"📺 {author}")
    lines.append(link)
    return "\n".join(lines)

def telegram_send(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "false",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("ok", False)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        log(f"[error] telegram HTTP {e.code}: {detail}", error=True)
        return False
    except Exception as e:
        log(f"[error] telegram send failed: {e}", error=True)
        return False

def download_audio(video_id: str, output_dir: str) -> str | None:
    """Download audio using yt-dlp and return the resulting file path."""
    outtmpl = os.path.join(output_dir, "audio.%(ext)s")
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "opus",
        "--no-playlist",
        "-o", outtmpl,
        f"https://youtu.be/{video_id}",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    except FileNotFoundError:
        log("[error] yt-dlp not found on system. Install it or disable voice.", error=True)
        return None
    except subprocess.CalledProcessError as e:
        log(f"[warn] yt-dlp failed for {video_id}: {e.stderr.decode('utf-8', 'replace')[:200]}", error=True)
        return None
    except subprocess.TimeoutExpired:
        log(f"[warn] yt-dlp timed out for {video_id}", error=True)
        return None

    files = glob.glob(os.path.join(output_dir, "audio.*"))
    if not files:
        log(f"[warn] yt-dlp produced no file for {video_id}", error=True)
        return None
    return files[0]

def telegram_send_voice(token: str, chat_id: str, video_id: str, title: str) -> bool:
    """Download audio and send as a Telegram voice message (multipart/form-data)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = download_audio(video_id, tmpdir)
        if not audio_path:
            return False

        boundary = "----TelegramBoundary" + uuid.uuid4().hex
        parts: list[str] = []

        def add_field(name: str, value: str) -> None:
            parts.append(f"--{boundary}")
            parts.append(f'Content-Disposition: form-data; name="{name}"')
            parts.append("")
            parts.append(value)

        add_field("chat_id", str(chat_id))
        add_field("caption", f"🎬 <b>{html.escape(title)}</b>")

        parts.append(f"--{boundary}")
        parts.append(f'Content-Disposition: form-data; name="voice"; filename="audio.ogg"')
        parts.append("Content-Type: audio/ogg")
        parts.append("")

        body_start = "\r\n".join(parts).encode("utf-8") + b"\r\n"
        with open(audio_path, "rb") as f:
            file_data = f.read()
        body_end = f"\r\n--{boundary}--\r\n".encode("utf-8")
        body = body_start + file_data + body_end

        url = f"https://api.telegram.org/bot{token}/sendVoice"
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("ok", False)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            log(f"[error] telegram sendVoice HTTP {e.code}: {detail}", error=True)
            return False
        except Exception as e:
            log(f"[error] telegram sendVoice failed: {e}", error=True)
            return False

# --- Modes -----------------------------------------------------------------

def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        log(f"[fatal] environment variable {name} is not set", error=True)
        sys.exit(2)
    return val

def run_test() -> int:
    token = require_env("TELEGRAM_BOT_TOKEN")
    chat_id = require_env("TELEGRAM_CHAT_ID")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    text = (
        "✅ <b>Connection established</b>\n\n"
        f"🕒 {now}\n"
        "This is a test message from yt-telegram-notifier."
    )
    ok = telegram_send(token, chat_id, text)
    if ok:
        log("test message sent successfully")
        return 0
    log("test message failed", error=True)
    return 1

def run_seed() -> int:
    specs = read_channels(CHANNELS_PATH)
    if not specs:
        log("[warn] no channels configured")
        return 0

    state = {"channels": {}}
    for spec in specs:
        cid = resolve_channel_id(spec)
        if not cid:
            log(f"[warn] skipping unresolvable channel: {spec}", error=True)
            continue
        try:
            entries = parse_feed(fetch(FEED_URL.format(cid=cid)))
        except Exception as e:
            log(f"[warn] failed to fetch {spec}: {e}", error=True)
            continue
        state["channels"][spec] = {
            "id": cid,
            "seen": [e["id"] for e in entries][:MAX_SEEN_PER_CHANNEL],
        }
        log(f"seeded {spec} ({cid}) with {len(entries)} entries")

    save_state(STATE_PATH, state)
    log(f"state written to {STATE_PATH}")
    return 0

def run_notify(*, dry_run: bool = False) -> int:
    token = require_env("TELEGRAM_BOT_TOKEN")
    chat_id = require_env("TELEGRAM_CHAT_ID")

    specs = read_channels(CHANNELS_PATH)
    if not specs:
        log("[warn] no channels configured in " + CHANNELS_PATH)
        return 0

    state = load_state(STATE_PATH)
    channels_state: dict = state.setdefault("channels", {})

    total_text = 0
    total_voice = 0
    total_failed = 0

    for spec in specs:
        cached = channels_state.get(spec, {}).get("id")
        cid = cached or resolve_channel_id(spec)
        if not cid:
            log(f"[warn] cannot resolve channel: {spec}", error=True)
            continue

        try:
            entries = parse_feed(fetch(FEED_URL.format(cid=cid)))
        except Exception as e:
            log(f"[warn] feed fetch failed for {spec} ({cid}): {e}", error=True)
            continue

        if spec not in channels_state:
            channels_state[spec] = {
                "id": cid,
                "seen": [e["id"] for e in entries][:MAX_SEEN_PER_CHANNEL],
            }
            log(f"[init] new channel seeded silently: {spec} ({len(entries)} entries)")
            continue

        seen = set(channels_state[spec].get("seen", []))
        fresh = [e for e in entries if e["id"] not in seen]
        fresh.reverse()

        if not fresh:
            vlog(f"[ok] {spec}: no new videos")
        else:
            log(f"[new] {spec}: {len(fresh)} new video(s)")

        for video in fresh:
            if dry_run:
                log(f"  [dry-run] would send: {video['title']} ({video['id']})")
                continue

            # 1. Text message
            if telegram_send(token, chat_id, format_message(video)):
                total_text += 1
                vlog(f"  [sent text] {video['id']}")
            else:
                total_failed += 1

            # 2. Voice message
            if VOICE_ENABLED:
                vlog(f"  [downloading voice] {video['id']}...")
                if telegram_send_voice(token, chat_id, video["id"], video["title"]):
                    total_voice += 1
                    vlog(f"  [sent voice] {video['id']}")
                else:
                    log(f"[warn] failed to send voice for {video['id']}", error=True)

            time.sleep(SEND_DELAY_SECONDS)

        merged = [e["id"] for e in entries]
        for vid in channels_state[spec].get("seen", []):
            if vid not in merged:
                merged.append(vid)
        channels_state[spec] = {
            "id": cid,
            "seen": merged[:MAX_SEEN_PER_CHANNEL],
        }

    if dry_run:
        log("[dry-run] done.")
        return 0

    save_state(STATE_PATH, state)
    log(f"done. text={total_text} voice={total_voice} failed={total_failed}")
    return 0 if total_failed == 0 else 1

# --- Entry point -----------------------------------------------------------

def main() -> int:
    global VERBOSE

    parser = argparse.ArgumentParser(description="Send new YouTube videos to Telegram.")
    parser.add_argument("--dry-run", action="store_true", help="show what would be sent")
    parser.add_argument("--test", action="store_true", help="send a test message")
    parser.add_argument("--seed", action="store_true", help="rebuild state silently")
    parser.add_argument("--verbose", "-v", action="store_true", help="extra diagnostics")
    args = parser.parse_args()

    VERBOSE = args.verbose

    if args.test:
        return run_test()
    if args.seed:
        return run_seed()
    return run_notify(dry_run=args.dry_run)

if __name__ == "__main__":
    sys.exit(main())

