"""
GitHub Repository Scanner for STALKER Anomaly Mods

Searches GitHub's public API for repositories that are likely mods for
the game S.T.A.L.K.E.R.: Anomaly. Results are scored by relevance and
saved to ../data/repos.json.

Usage:
    python scanner.py [--output PATH] [--min-score N] [--no-details]

Requirements:
    pip install -r requirements.txt

Optional:
    Copy .env.example to .env and set GITHUB_TOKEN for higher rate limits.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"
OUTPUT_DIR = Path(__file__).parent.parent / "data"

# ---------------------------------------------------------------------------
# Search queries — each tuple is (query_string, boost_score)
# GitHub Search API supports: in:name, in:description, in:topics
# ---------------------------------------------------------------------------
SEARCH_QUERIES = [
    # Direct topic matches (highest confidence)
    ("topic:stalker-anomaly", 30),
    ("topic:stalker-gamma", 25),
    ("topic:anomaly-mod", 25),
    ("topic:xray-engine", 10),
    ("topic:stalker-mod", 20),
    # Name/description keyword combos
    ("stalker anomaly mod in:name,description", 20),
    ("stalker anomaly in:name", 15),
    ("anomaly mod stalker in:description", 15),
    ("S.T.A.L.K.E.R anomaly in:name,description", 20),
    ("GAMMA stalker anomaly in:description", 15),
    # Anomaly-specific file/script patterns via code search aren't available
    # without auth, so we use description heuristics instead
    ("anomaly addon in:name,description stalker", 15),
    ("stalker gamma mod in:name,description", 15),
    ("xray engine mod stalker in:name,description", 10),
]

# ---------------------------------------------------------------------------
# Scoring signals applied on top of the base query boost
# ---------------------------------------------------------------------------

# Keywords in name/description → extra points
KEYWORD_SIGNALS = {
    "stalker": 5,
    "anomaly": 8,
    "s.t.a.l.k.e.r": 10,
    "gamma": 5,
    "xray": 4,
    "x-ray": 4,
    "gamedata": 8,   # canonical Anomaly mod folder name
    "addon": 4,
    "mod": 3,
    "script": 3,
    "lua": 3,
    "configs": 3,
}

# Topics on the repo → extra points
TOPIC_SIGNALS = {
    "stalker-anomaly": 20,
    "stalker-gamma": 15,
    "anomaly-mod": 15,
    "stalker-mod": 10,
    "xray-engine": 8,
    "stalker": 8,
    "anomaly": 10,
    "lua": 3,
    "game-mod": 5,
    "modding": 4,
}

# Languages that indicate real mod code (vs. just documentation repos)
CODE_LANGUAGE_BONUS = {
    "Lua": 10,
    "XML": 5,
    "C++": 3,
    "Python": 2,
}

# Repos with these in their full_name are almost certainly noise
BLOCKLIST_TERMS = [
    "chernobyl",     # often unrelated Chernobyl content
    "tutorial",      # generic tutorials not specific to Anomaly
]


def make_session(token: str | None) -> requests.Session:
    session = requests.Session()
    session.headers["Accept"] = "application/vnd.github+json"
    session.headers["X-GitHub-Api-Version"] = "2022-11-28"
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    return session


def search_repos(session: requests.Session, query: str, max_pages: int = 10) -> list[dict]:
    """Paginate through GitHub repo search results for a single query."""
    results = []
    page = 1
    per_page = 100

    while page <= max_pages:
        url = f"{GITHUB_API}/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page,
        }
        resp = session.get(url, params=params, timeout=30)

        if resp.status_code == 422:
            print(f"  [skip] Query not valid: {query}")
            break

        if resp.status_code == 403:
            reset_ts = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset_ts - int(time.time()), 1)
            print(f"  [rate limit] Waiting {wait}s...")
            time.sleep(wait + 1)
            continue

        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        results.extend(items)

        # GitHub caps at 1000 results per query regardless of pagination
        total = data.get("total_count", 0)
        fetched = (page - 1) * per_page + len(items)
        print(f"  Page {page}: got {len(items)} (total available: {total}, fetched so far: {fetched})")

        if len(items) < per_page or fetched >= min(total, 1000):
            break

        page += 1

        # Respect secondary rate limits — GitHub recommends ≥1s between requests
        remaining = int(resp.headers.get("X-RateLimit-Remaining", 1))
        if remaining < 5:
            reset_ts = int(resp.headers.get("X-RateLimit-Reset", time.time() + 10))
            wait = max(reset_ts - int(time.time()), 1)
            print(f"  [rate limit low] Waiting {wait}s...")
            time.sleep(wait + 1)
        else:
            time.sleep(1)

    return results


def score_repo(repo: dict, base_boost: int) -> int:
    """Calculate a relevance score for a repository."""
    score = base_boost
    name = (repo.get("name") or "").lower()
    description = (repo.get("description") or "").lower()
    combined = f"{name} {description}"
    topics = [t.lower() for t in (repo.get("topics") or [])]
    language = repo.get("language") or ""

    for kw, pts in KEYWORD_SIGNALS.items():
        if kw in combined:
            score += pts

    for topic, pts in TOPIC_SIGNALS.items():
        if topic in topics:
            score += pts

    score += CODE_LANGUAGE_BONUS.get(language, 0)

    # Penalise archived repos slightly
    if repo.get("archived"):
        score -= 5

    # Small bonus for repos with actual stars (indicates real usage)
    stars = repo.get("stargazers_count", 0)
    if stars >= 100:
        score += 10
    elif stars >= 20:
        score += 5
    elif stars >= 5:
        score += 2

    return score


def is_blocklisted(repo: dict) -> bool:
    full_name = (repo.get("full_name") or "").lower()
    description = (repo.get("description") or "").lower()
    for term in BLOCKLIST_TERMS:
        if term in full_name and "stalker" not in full_name:
            return True
    return False


def get_repo_details(session: requests.Session, full_name: str) -> dict:
    """Fetch additional details: README existence, top-level file listing."""
    details = {"has_gamedata": False, "has_lua_scripts": False, "readme_snippet": ""}

    # Check default branch tree for gamedata/ folder
    try:
        url = f"{GITHUB_API}/repos/{full_name}/git/trees/HEAD"
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            tree = resp.json().get("tree", [])
            top_level = {entry["path"].lower() for entry in tree}
            details["has_gamedata"] = "gamedata" in top_level
            details["top_level_dirs"] = sorted(
                [e["path"] for e in tree if e["type"] == "tree"][:20]
            )
    except Exception:
        pass

    time.sleep(0.5)
    return details


def deduplicate(repos: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for repo in repos:
        rid = repo["id"]
        if rid not in seen:
            seen.add(rid)
            unique.append(repo)
    return unique


def normalize_repo(repo: dict, score: int) -> dict:
    """Extract only the fields we care about from a raw GitHub API response."""
    return {
        "id": repo["id"],
        "full_name": repo["full_name"],
        "html_url": repo["html_url"],
        "description": repo.get("description") or "",
        "topics": repo.get("topics") or [],
        "language": repo.get("language") or "",
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "archived": repo.get("archived", False),
        "pushed_at": repo.get("pushed_at") or "",
        "created_at": repo.get("created_at") or "",
        "relevance_score": score,
        # Details filled in later if --no-details is not set
        "has_gamedata": None,
        "top_level_dirs": [],
    }


def main():
    parser = argparse.ArgumentParser(description="Scan GitHub for STALKER Anomaly mod repos")
    parser.add_argument("--output", default=str(OUTPUT_DIR / "repos.json"), help="Output JSON path")
    parser.add_argument("--min-score", type=int, default=20, help="Minimum relevance score to include (default: 20)")
    parser.add_argument("--no-details", action="store_true", help="Skip per-repo detail fetching (faster, less accurate)")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("WARNING: No GITHUB_TOKEN set. Rate limits will be strict (10 req/min).")
        print("         Copy .env.example to .env and add your token for better results.\n")

    session = make_session(token)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Phase 1: Search ---
    print(f"=== Phase 1: Searching GitHub ({len(SEARCH_QUERIES)} queries) ===")
    raw_repos: list[tuple[dict, int]] = []  # (repo_dict, base_boost)

    for i, (query, boost) in enumerate(SEARCH_QUERIES, 1):
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] Query: {query!r}  (base boost: {boost})")
        items = search_repos(session, query)
        for item in items:
            raw_repos.append((item, boost))
        print(f"  => {len(items)} results")

    print(f"\nTotal raw results (with duplicates): {len(raw_repos)}")

    # --- Phase 2: Score & deduplicate ---
    print("\n=== Phase 2: Scoring & deduplicating ===")
    # For repos that appear in multiple queries, accumulate score boosts
    score_map: dict[int, int] = {}
    repo_map: dict[int, dict] = {}

    for repo, boost in raw_repos:
        rid = repo["id"]
        incremental_score = score_repo(repo, boost)
        if rid in score_map:
            # Add partial boost for duplicate hits (diminishing returns)
            score_map[rid] += boost // 2
        else:
            score_map[rid] = incremental_score
            repo_map[rid] = repo

    results = [
        normalize_repo(repo, score_map[rid])
        for rid, repo in repo_map.items()
        if score_map[rid] >= args.min_score and not is_blocklisted(repo)
    ]
    results.sort(key=lambda r: r["relevance_score"], reverse=True)
    print(f"After dedup & min-score filter ({args.min_score}): {len(results)} repos")

    # --- Phase 3: Enrich with per-repo details ---
    if not args.no_details:
        print(f"\n=== Phase 3: Fetching repo details ({len(results)} repos) ===")
        for i, repo in enumerate(results, 1):
            print(f"  [{i}/{len(results)}] {repo['full_name']}")
            details = get_repo_details(session, repo["full_name"])
            repo.update(details)
            if details.get("has_gamedata"):
                repo["relevance_score"] += 15  # strong signal: gamedata/ present
                print(f"    => has gamedata/ folder (+15 score)")
        # Re-sort after score adjustments
        results.sort(key=lambda r: r["relevance_score"], reverse=True)

    # --- Save ---
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_repos": len(results),
        "min_score_filter": args.min_score,
        "repos": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n=== Done ===")
    print(f"Saved {len(results)} repos to {output_path}")
    print(f"\nTop 20 by relevance score:")
    for repo in results[:20]:
        gamedata = "[gamedata]" if repo.get("has_gamedata") else ""
        print(f"  {repo['relevance_score']:3d}  {repo['full_name']:50s}  *{repo['stars']:<5d}  {gamedata}")


if __name__ == "__main__":
    main()
