"""
Downloads the Basketball Reference pages I need and saves the raw html in data/raw/html/.

Pulling the tables out of the html happens in a separate script (parse.py), so if I mess
up the parsing I don't have to scrape everything again.

bbref blocks you for up to a day if you go over 20 requests a minute, so this waits
between every request. A full run takes around 10 minutes.
"""
import time
from pathlib import Path

import requests

HTML_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "html"
BASE_URL = "https://www.basketball-reference.com/leagues"

# 1980 is the first season with the 3 point line
FIRST_SEASON = 1980
# bbref names a season by the year it ends, so 2026 means the 2025-26 season
LAST_SEASON = 2026

# 4 seconds between requests = 15 a minute, safely under their limit of 20
DELAY_SECONDS = 4

# tell them who's asking instead of showing up as a generic python script
HEADERS = {"User-Agent": "nba-lineup-predictor (personal project, github.com/mare18explore)"}

# the 3 pages I want for every season. the value is what goes after NBA_2024 in the url
PAGES = {
    "summary": "",            # standings + team stats
    "advanced": "_advanced",  # player advanced stats (BPM, win shares, usage...)
    "per_game": "_per_game",  # player points, rebounds, assists per game
}


def fetch(url, out_path):
    resp = requests.get(url, headers=HEADERS, timeout=30)

    # 429 = too many requests. if we keep going we just stay blocked longer, so stop
    if resp.status_code == 429:
        raise SystemExit("got rate limited (429), wait a while before running this again")

    resp.raise_for_status()
    out_path.write_bytes(resp.content)


def main():
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    for season in range(FIRST_SEASON, LAST_SEASON + 1):
        for page_name, suffix in PAGES.items():
            out_path = HTML_DIR / f"{season}_{page_name}.html"

            # already saved from an earlier run, so if it crashes halfway I can just rerun it
            if out_path.exists():
                continue

            url = f"{BASE_URL}/NBA_{season}{suffix}.html"
            print(f"{season} {page_name}")
            fetch(url, out_path)
            time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()