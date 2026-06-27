#!/usr/bin/env python3
"""Rebuild rss.xml from notes/index.generated.combined.json.

Usage:
    python3 scripts/rebuild-rss.py [--base-url https://example.com]

The base URL is auto-detected from a running localtunnel process.
If none is running, pass --base-url explicitly.
"""

import json
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = SITE_ROOT / "notes" / "index.generated.combined.json"
RSS_PATH = SITE_ROOT / "rss.xml"

IST_OFFSET = "+0530"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def detect_base_url() -> str:
    """Try to find a running localtunnel URL."""
    # 1. Check saved tunnel URL file
    url_file = SITE_ROOT / ".tunnel_url"
    try:
        if url_file.exists():
            url = url_file.read_text().strip()
            if url.startswith("https://"):
                return url
    except Exception:
        pass

    # 2. Scan running processes for lt/localtunnel
    try:
        result = subprocess.run(
            ["pgrep", "-af", r"lt --port|localtunnel"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            m = re.search(r'https://([a-z-]+\.loca\.lt)', line)
            if m:
                return f"https://{m.group(1)}"
    except Exception:
        pass
    return ""


def format_rfc2822(date_str: str) -> str:
    """Convert YYYY-MM-DD to RFC 2822 format with IST offset."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{DAYS[dt.weekday()]}, {dt.day:02d} {MONTHS[dt.month - 1]} {dt.year} 00:00:00 {IST_OFFSET}"


def extract_description(html_path: Path) -> str:
    """Extract the first meaningful <p> inside <main>."""
    html = html_path.read_text(encoding="utf-8")
    mm = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL)
    if not mm:
        return ""
    for pm in re.finditer(r"<p[^>]*>(.*?)</p>", mm.group(1), re.DOTALL):
        raw = pm.group(1).strip()
        plain = re.sub(r"<[^>]+>", "", raw).strip()
        if plain:
            return re.sub(r"\s+", " ", raw).strip()
    return ""


def xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_rss(base_url: str) -> str:
    notes = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    last_build = format_rfc2822(notes[0]["date"]) if notes else ""

    items = []
    for note in notes:
        name = note["name"]
        note_path = SITE_ROOT / "notes" / name / "index.html"
        desc = extract_description(note_path) if note_path.exists() else ""
        pubdate = format_rfc2822(note["date"])
        link = f"{base_url}/notes/{name}/"

        cats = "\n".join(f"      <category>{xml_escape(t)}</category>" for t in note.get("tags", []))

        item = f"""    <item>
      <title>{xml_escape(note['title'])}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pubdate}</pubDate>
      <description><![CDATA[<p>{desc}</p>]]></description>
{cats}
    </item>"""
        items.append(item)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Vishnu Nair — Security Research Notes</title>
    <link>{base_url}</link>
    <description>Deep-dive security research, vulnerability case studies, and technical breakdowns.</description>
    <language>en-us</language>
    <lastBuildDate>{last_build}</lastBuildDate>
    <atom:link href="{base_url}/rss.xml" rel="self" type="application/rss+xml"/>

{chr(10).join(items)}

  </channel>
</rss>
"""


def main():
    base_url = None

    # Parse --base-url flag
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--base-url" and i + 1 < len(args):
            base_url = args[i + 1].rstrip("/")

    if not base_url:
        base_url = detect_base_url()

    if not base_url:
        print("ERROR: No base URL found. Pass --base-url or start localtunnel.", file=sys.stderr)
        sys.exit(1)

    rss = build_rss(base_url)
    RSS_PATH.write_text(rss, encoding="utf-8")
    print(f"✓ rss.xml rebuilt — {base_url}/rss.xml")


if __name__ == "__main__":
    main()
