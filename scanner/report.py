"""
Quick report generator — prints a human-readable summary from repos.json
and/or the analysis index.

Usage:
    python report.py                    # summary of repos.json
    python report.py --analysis         # include callback/API index
    python report.py --top 100          # show top 100 repos
"""

import argparse
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos", default=str(DATA_DIR / "repos.json"))
    parser.add_argument("--analysis", action="store_true")
    parser.add_argument("--top", type=int, default=50)
    args = parser.parse_args()

    repos_path = Path(args.repos)
    if not repos_path.exists():
        print("No repos.json found. Run scanner.py first.")
        return

    with open(repos_path, encoding="utf-8") as f:
        data = json.load(f)

    print(f"Scan generated: {data['generated_at']}")
    print(f"Total repos found: {data['total_repos']}")
    print()

    repos = data["repos"][: args.top]
    print(f"{'Score':>5}  {'Stars':>5}  {'Gamedata':>8}  {'Language':<10}  Name")
    print("-" * 90)
    for r in repos:
        gd = "yes" if r.get("has_gamedata") else ("?" if r.get("has_gamedata") is None else "no")
        lang = (r.get("language") or "")[:10]
        print(f"{r['relevance_score']:5d}  {r['stars']:5d}  {gd:>8}  {lang:<10}  {r['full_name']}")
        if r.get("description"):
            print(f"         {r['description'][:80]}")

    if args.analysis:
        index_path = DATA_DIR / "analysis" / "index.json"
        if not index_path.exists():
            print("\nNo analysis index found. Run analyze_repos.py first.")
            return

        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)

        print("\n\n=== Top Callbacks (by frequency across repos) ===")
        for cb, count in list(index["callbacks_by_frequency"].items())[:50]:
            print(f"  {count:4d}x  {cb}")

        print("\n=== Top API Calls ===")
        for call, count in list(index["api_calls_by_frequency"].items())[:30]:
            print(f"  {count:4d}x  {call}")


if __name__ == "__main__":
    main()
