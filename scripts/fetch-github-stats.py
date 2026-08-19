#!/usr/bin/env python3
"""Fetch GitHub contributions for drago-nair and update site data files.

Uses the GITHUB_TOKEN from /opt/data/site/.env (gitignored).
Updates:
  - data/gh-contribs.json   (heatmap matrix: N weeks x 7 days, levels 0-4)
  - data/github-stats.json  (week, year_total, updated)
"""
import json
import os
import re
import subprocess
import urllib.request
from datetime import datetime, timedelta

SITE = "/opt/data/site"
ENV = os.path.join(SITE, ".env")
WEEKS = 4  # number of columns in the heatmap

def load_token():
    if not os.path.exists(ENV):
        raise SystemExit("No .env file — set GITHUB_TOKEN in /opt/data/site/.env")
    with open(ENV) as f:
        for line in f:
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("GITHUB_TOKEN not found in .env")

def gql(token, query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "portfolio-refresh",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def level_for(n):
    # scaled for a modest-volume account
    if n <= 0:
        return 0
    if n <= 1:
        return 1
    if n <= 3:
        return 2
    if n <= 5:
        return 3
    return 4

def main():
    token = load_token()
    query = """
    query {
      viewer {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }
    """
    data = gql(token, query)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    cal = data["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]

    days = [cd for w in cal["weeks"] for cd in w["contributionDays"]]
    counts = {cd["date"]: cd["contributionCount"] for cd in days}

    now = datetime.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    year_start = datetime(now.year, 1, 1).date()

    week_total = sum(v for d, v in counts.items() if datetime.fromisoformat(d).date() >= week_start)
    year_total = sum(v for d, v in counts.items() if datetime.fromisoformat(d).date() >= year_start)

    # Build heatmap matrix: last WEEKS weeks, aligned to weeks (Sunday-Saturday)
    # GitHub weeks start on Sunday.
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    matrix = []
    for w in range(WEEKS - 1, -1, -1):
        week_start_day = last_sunday - timedelta(weeks=w)
        col = []
        for i in range(7):
            d = (week_start_day + timedelta(days=i)).isoformat()
            col.append(level_for(counts.get(d, 0)))
        matrix.append(col)

    contribs_path = os.path.join(SITE, "data", "gh-contribs.json")
    stats_path = os.path.join(SITE, "data", "github-stats.json")

    with open(contribs_path, "w") as f:
        json.dump(matrix, f)

    stats = {
        "week": week_total,
        "last_week": week_total,
        "year_total": year_total,
        "updated": today.isoformat(),
    }
    with open(stats_path, "w") as f:
        json.dump(stats, f)

    print(f"week={week_total} year_total={year_total} total={cal['totalContributions']}")
    print(f"wrote {contribs_path} ({WEEKS} weeks) and {stats_path}")

if __name__ == "__main__":
    main()
