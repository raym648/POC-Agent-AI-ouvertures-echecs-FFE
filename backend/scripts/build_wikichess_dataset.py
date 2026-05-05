# POC-Agent-AI-ouvertures-echecs-FFE/scripts/build_wikichess_dataset.py

"""
Build wikichess_sample.json from real public chess opening sources.

Primary source (semantic corpus):
- FICGS / Wikichess opening articles
  - https://ficgs.com/directory_openings.html
  - https://ficgs.com/wikichess_1.html

Secondary source (taxonomy):
- Lichess public ECO TSV shards
  - https://raw.githubusercontent.com/lichess-org/chess-openings/master/{a,b,c,d,e}.tsv

Tertiary source (statistics):
- Lichess Opening Explorer API
  - https://explorer.lichess.ovh/lichess

Output:
- data/chess/wikichess_sample.json

Goal:
Generate a structured chess opening dataset suitable for:
- semantic retrieval
- embeddings
- Milvus ingestion
- chess opening RAG
"""

from __future__ import annotations

import csv
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

try:
    import chess
except ImportError:
    chess = None


# -------------------------------------------------------------------
# Paths / config
# -------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "backend" / "data" / "chess"
OUTPUT_PATH = DATA_DIR / "wikichess_sample.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WikichessDatasetBuilder/5.0)"
}

FICGS_INDEX_URLS = [
    "https://ficgs.com/directory_openings.html",
    "https://ficgs.com/wikichess_1.html",
]

# Valid and accessible public ECO shards
ECO_TSV_URLS = [
    "https://raw.githubusercontent.com/lichess-org/chess-openings/master/a.tsv",
    "https://raw.githubusercontent.com/lichess-org/chess-openings/master/b.tsv",
    "https://raw.githubusercontent.com/lichess-org/chess-openings/master/c.tsv",
    "https://raw.githubusercontent.com/lichess-org/chess-openings/master/d.tsv",
    "https://raw.githubusercontent.com/lichess-org/chess-openings/master/e.tsv",
]

# Correct JSON Opening Explorer endpoint
# LICHESS_URL = "https://explorer.lichess.ovh/lichess"
# LICHESS_URL = "https://lichess.org/opening"
LICHESS_URL = "https://lichess.org/api"

REQUEST_TIMEOUT = 20
MAX_ARTICLES = 200
SLEEP_SECONDS = 0.35


# -------------------------------------------------------------------
# Data model
# -------------------------------------------------------------------

@dataclass
class OpeningEntry:
    id: str
    eco: str
    opening: str
    variation: str
    line_san: str
    position_fen: str
    candidate_moves: List[Dict]
    stats: Dict
    explanation: str
    source_url: str
    search_text: str


# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------

def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def sanitize_variation(value: str) -> str:
    value = normalize_spaces(value)
    return value if value else "Main Line"


def clean_text(text: str) -> str:
    text = normalize_spaces(text)
    text = re.sub(r"\s*Advertisement\s*", " ", text, flags=re.I)
    text = re.sub(r"\s*Back to.*?$", "", text, flags=re.I)
    text = re.sub(r"\s*Cookie\s*Policy.*?$", "", text, flags=re.I)
    return normalize_spaces(text)


def extract_first_san_line(text: str) -> str:
    patterns = [
        r"(1\.\s?[A-Za-z0-9+=#-]+(?:\s+[A-Za-z0-9+=#-]+){1,20})",
        r"(1\.[A-Za-z0-9+=#-]+(?:\s+[A-Za-z0-9+=#-]+){1,20})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return normalize_spaces(match.group(1))
    return ""


def build_explanation(opening: str, variation: str, article_text: str) -> str:
    article_text = clean_text(article_text)
    if len(article_text) > 900:
        article_text = article_text[:900]
    prefix = f"{opening} ({variation}). "
    return normalize_spaces(prefix + article_text)


def build_search_text(entry: OpeningEntry) -> str:
    candidate_blob = ", ".join(
        f"{m['san']} ({m['games']} games, W {m['white_win']}%, D {m['draw']}%, B {m['black_win']}%)"
        for m in entry.candidate_moves[:5]
    )
    return normalize_spaces(
        (
            f"{entry.opening}. {entry.variation}. ECO {entry.eco}. "
            f"Line {entry.line_san}. "
            f"{entry.explanation}. "
            f"Candidate moves: {candidate_blob}"
        )
    )[:4096]


def compute_fen_from_line(line_san: str) -> str:
    if not chess or not line_san:
        return ""

    board = chess.Board()

    try:
        tokens = line_san.split()
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            if re.match(r"^\d+\.$", token):
                continue
            token = re.sub(r"^\d+\.", "", token)
            if not token:
                continue
            board.push_san(token)
        return board.fen()
    except Exception:
        return ""


# -------------------------------------------------------------------
# Remote helpers
# -------------------------------------------------------------------

def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def fetch_json(url: str, params: Optional[dict] = None) -> dict:
    resp = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# -------------------------------------------------------------------
# ECO taxonomy
# -------------------------------------------------------------------

def load_eco_index() -> List[Dict]:
    rows: List[Dict] = []

    for url in ECO_TSV_URLS:
        try:
            content = fetch(url)
        except Exception as e:
            print(f"⚠️ Failed to fetch ECO shard {url}: {e}")
            continue

        reader = csv.reader(content.splitlines(), delimiter="\t")

        for i, row in enumerate(reader):
            if not row:
                continue

            if i == 0:
                continue  # skip header

            if len(row) < 3:
                continue

            eco = normalize_spaces(row[0])
            name = normalize_spaces(row[1])
            pgn = normalize_spaces(row[2])

            if ":" in name:
                opening, variation = [x.strip() for x in name.split(":", 1)]
            else:
                opening, variation = name, "Main Line"

            rows.append(
                {
                    "eco": eco,
                    "opening": opening,
                    "variation": sanitize_variation(variation),
                    "line_san": pgn,
                }
            )

    return rows


def match_eco(opening_name: str, eco_rows: List[Dict]) -> Tuple[str, str, str, str]:
    target = normalize_spaces(opening_name).lower()

    for row in eco_rows:
        if row["opening"].lower() == target:
            return row["eco"], row["opening"], row["variation"], row["line_san"]

    for row in eco_rows:
        if target in row["opening"].lower() or row["opening"].lower() in target:
            return row["eco"], row["opening"], row["variation"], row["line_san"]

    return "UNK", opening_name, "Main Line", ""


# -------------------------------------------------------------------
# FICGS / Wikichess crawl
# -------------------------------------------------------------------

def discover_article_urls() -> List[str]:
    urls = set()

    for index_url in FICGS_INDEX_URLS:
        try:
            html = fetch(index_url)
        except Exception as e:
            print(f"⚠️ Failed to fetch index {index_url}: {e}")
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            label = normalize_spaces(a.get_text(" ", strip=True))

            if not href:
                continue

            full_url = urljoin(index_url, href)

            if "ficgs.com" not in full_url:
                continue

            if not label:
                continue

            if (
                "opening" in full_url.lower()
                or "wikichess" in full_url.lower()
                or "defense" in label.lower()
                or "gambit" in label.lower()
                or "opening" in label.lower()
                or "attack" in label.lower()
            ):
                urls.add(full_url)

    return sorted(urls)[:MAX_ARTICLES]


def parse_article(url: str, eco_rows: List[Dict]) -> Optional[OpeningEntry]:
    try:
        html = fetch(url)
    except Exception:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = normalize_spaces(soup.title.get_text()) if soup.title else ""
    h1 = normalize_spaces(soup.find("h1").get_text()) if soup.find("h1") else ""
    opening_name = h1 or title.split("-")[0].strip()

    text = clean_text(soup.get_text(" ", strip=True))
    if len(text) < 200:
        return None

    line_san = extract_first_san_line(text)

    eco, opening, variation, fallback_line = match_eco(opening_name, eco_rows)

    if not line_san:
        line_san = fallback_line

    position_fen = compute_fen_from_line(line_san)

    entry = OpeningEntry(
        id=f"{eco.lower()}_{slugify(opening)}_{slugify(variation)}",
        eco=eco,
        opening=opening,
        variation=variation,
        line_san=line_san,
        position_fen=position_fen,
        candidate_moves=[],
        stats={"games": 0, "white_win": 0.0, "draw": 0.0, "black_win": 0.0},
        explanation=build_explanation(opening, variation, text),
        source_url=url,
        search_text="",
    )

    entry.search_text = build_search_text(entry)
    return entry


# -------------------------------------------------------------------
# Lichess enrichment
# -------------------------------------------------------------------

def enrich_with_lichess(entry: OpeningEntry) -> OpeningEntry:
    if not entry.line_san:
        return entry

    play = []
    for token in entry.line_san.split():
        if re.match(r"^\d+\.$", token):
            continue
        token = re.sub(r"^\d+\.", "", token)
        if token:
            play.append(token)

    if not play:
        return entry

    params = {
        "play": ",".join(play),
        "moves": 5,
        "topGames": 0,
        "recentGames": 0,
    }

    try:
        data = fetch_json(LICHESS_URL, params=params)
    except Exception:
        return entry

    candidate_moves = []

    for move in data.get("moves", [])[:5]:
        total = move["white"] + move["draws"] + move["black"]
        if total == 0:
            continue

        candidate_moves.append(
            {
                "san": move["san"],
                "games": total,
                "white_win": round((move["white"] / total) * 100, 1),
                "draw": round((move["draws"] / total) * 100, 1),
                "black_win": round((move["black"] / total) * 100, 1),
            }
        )

    if candidate_moves:
        entry.candidate_moves = candidate_moves
        entry.stats = {
            "games": sum(m["games"] for m in candidate_moves),
            "white_win": round(sum(m["white_win"] for m in candidate_moves) / len(candidate_moves), 1),
            "draw": round(sum(m["draw"] for m in candidate_moves) / len(candidate_moves), 1),
            "black_win": round(sum(m["black_win"] for m in candidate_moves) / len(candidate_moves), 1),
        }

    entry.search_text = build_search_text(entry)
    return entry


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> None:
    print("♟️ Loading ECO taxonomy...")
    eco_rows = load_eco_index()
    print(f"Loaded ECO rows: {len(eco_rows)}")

    print("🌐 Discovering Wikichess articles...")
    article_urls = discover_article_urls()
    print(f"Discovered article URLs: {len(article_urls)}")

    dataset: Dict[str, Dict] = {}

    for i, url in enumerate(article_urls, start=1):
        print(f"[{i}/{len(article_urls)}] Parsing {url}")

        entry = parse_article(url, eco_rows)
        if not entry:
            continue

        entry = enrich_with_lichess(entry)
        dataset[entry.id] = asdict(entry)

        time.sleep(SLEEP_SECONDS)

    final_dataset = list(dataset.values())

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)

    print(f"✅ Dataset generated: {OUTPUT_PATH} ({len(final_dataset)} entries)")


if __name__ == "__main__":
    main()
