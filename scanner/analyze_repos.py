"""
Anomaly Mod Repository Analyzer

Reads repos.json produced by scanner.py, then for each repo:
  - Clones it (shallow) into a local cache
  - Walks the file tree to extract Lua script patterns, callback names,
    function signatures, XML configs, and other modding primitives
  - Writes a summary per repo and a merged index of discovered API symbols

Usage:
    python analyze_repos.py [--repos PATH] [--cache-dir PATH] [--top N] [--skip-clone]

Output:
    ../data/analysis/
        <owner>__<repo>/     - per-repo summaries
        index.json           - merged symbol/callback index across all repos
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_REPOS_JSON = DATA_DIR / "repos.json"
DEFAULT_CACHE_DIR = DATA_DIR / "clones"
DEFAULT_ANALYSIS_DIR = DATA_DIR / "analysis"

# ---------------------------------------------------------------------------
# Patterns to extract from Lua scripts
# ---------------------------------------------------------------------------

# Anomaly callback registration: RegisterScriptCallback("on_xxx", fn)
RE_REGISTER_CALLBACK = re.compile(
    r'RegisterScriptCallback\s*\(\s*["\']([^"\']+)["\']\s*,',
    re.MULTILINE
)

# AddScriptCallback usage
RE_ADD_CALLBACK = re.compile(
    r'AddScriptCallback\s*\(\s*["\']([^"\']+)["\']',
    re.MULTILINE
)

# actor_on_*, npc_on_*, etc. callback patterns from function names
RE_CALLBACK_FUNC = re.compile(
    r'function\s+\w+\s*\.\s*(\w*on_\w+|actor_\w+|npc_\w+|monster_\w+|server_\w+)\s*\(',
    re.MULTILINE | re.IGNORECASE
)

# Top-level function definitions: function module.name(...)
RE_FUNCTION_DEF = re.compile(
    r'^function\s+([\w.]+)\s*\(([^)]*)\)',
    re.MULTILINE
)

# game_object / alife / level API calls: some_obj:method(
RE_METHOD_CALL = re.compile(
    r'\b(alife|db\.actor|level|game|xr_logic|utils|axr_\w+|ui_\w+)\s*[.:](\w+)\s*\(',
    re.MULTILINE
)

# ini_file reads: e.g. ini:r_string("section", "key")
RE_INI_READ = re.compile(
    r'\bini\s*:\s*(r_string|r_float|r_u32|r_s32|r_bool|line_exist|section_exist)\s*\(',
    re.MULTILINE
)

# XML/config section names from configs
RE_XML_CLASS = re.compile(r'<(\w+)\s+id=["\']([^"\']+)["\']', re.MULTILINE)


def clone_or_update(repo_url: str, dest: Path) -> bool:
    """Shallow-clone a repo if not present. Returns True on success."""
    if dest.exists():
        return True
    try:
        result = subprocess.run(
            ["git", "clone", "--depth=1", "--quiet", repo_url, str(dest)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            print(f"    [clone error] {result.stderr.strip()[:200]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("    [clone timeout]")
        return False
    except FileNotFoundError:
        print("    [git not found — install git and ensure it's on PATH]")
        return False


def iter_files(root: Path, extensions: set[str]):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            yield path


def analyze_lua_file(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}

    callbacks = set()
    callbacks.update(RE_REGISTER_CALLBACK.findall(text))
    callbacks.update(RE_ADD_CALLBACK.findall(text))
    callbacks.update(RE_CALLBACK_FUNC.findall(text))

    functions = RE_FUNCTION_DEF.findall(text)  # list of (name, params)
    api_calls = RE_METHOD_CALL.findall(text)    # list of (object, method)
    ini_reads = RE_INI_READ.findall(text)

    return {
        "callbacks": sorted(callbacks),
        "functions": [(n, p.strip()) for n, p in functions],
        "api_calls": [(obj, meth) for obj, meth in api_calls],
        "ini_read_types": sorted(set(ini_reads)),
    }


def analyze_repo(repo_dir: Path) -> dict:
    """Walk a cloned repo and extract modding patterns."""
    summary = {
        "callbacks": defaultdict(int),    # callback_name -> occurrence count
        "functions": [],                   # list of {file, name, params}
        "api_calls": defaultdict(int),     # "obj.method" -> count
        "ini_read_types": set(),
        "script_files": [],
        "config_files": [],
        "file_count": 0,
    }

    for lua_path in iter_files(repo_dir, {".lua", ".script"}):
        rel = lua_path.relative_to(repo_dir)
        summary["script_files"].append(str(rel))
        summary["file_count"] += 1
        result = analyze_lua_file(lua_path)  # works for both .lua and .script (both are Lua)

        for cb in result.get("callbacks", []):
            summary["callbacks"][cb] += 1

        for name, params in result.get("functions", []):
            summary["functions"].append({
                "file": str(rel),
                "name": name,
                "params": params,
            })

        for obj, meth in result.get("api_calls", []):
            summary["api_calls"][f"{obj}.{meth}"] += 1

        summary["ini_read_types"].update(result.get("ini_read_types", []))

    for xml_path in iter_files(repo_dir, {".xml", ".ltx"}):
        rel = xml_path.relative_to(repo_dir)
        summary["config_files"].append(str(rel))

    # Convert defaultdicts and sets for JSON serialisation
    summary["callbacks"] = dict(sorted(summary["callbacks"].items(), key=lambda x: -x[1]))
    summary["api_calls"] = dict(sorted(summary["api_calls"].items(), key=lambda x: -x[1]))
    summary["ini_read_types"] = sorted(summary["ini_read_types"])
    # Trim to top 500 functions to keep file size manageable
    summary["functions"] = summary["functions"][:500]
    summary["script_files"] = sorted(summary["script_files"])[:200]
    summary["config_files"] = sorted(summary["config_files"])[:200]

    return summary


def merge_index(per_repo: list[dict]) -> dict:
    """Build a cross-repo index of callbacks, API calls, and functions."""
    all_callbacks: dict[str, int] = defaultdict(int)
    all_api_calls: dict[str, int] = defaultdict(int)
    all_functions: dict[str, list[str]] = defaultdict(list)  # name -> list of (file, params)

    for entry in per_repo:
        repo_name = entry["repo"]
        data = entry["analysis"]
        for cb, count in data.get("callbacks", {}).items():
            all_callbacks[cb] += count
        for call, count in data.get("api_calls", {}).items():
            all_api_calls[call] += count
        for fn in data.get("functions", []):
            all_functions[fn["name"]].append(f"{repo_name}:{fn['file']}")

    return {
        "callbacks_by_frequency": dict(sorted(all_callbacks.items(), key=lambda x: -x[1])),
        "api_calls_by_frequency": dict(sorted(all_api_calls.items(), key=lambda x: -x[1])),
        "function_index": {
            name: {"seen_in": locs[:10]}
            for name, locs in sorted(all_functions.items())
            if len(locs) >= 2  # only cross-repo symbols
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze cloned STALKER Anomaly mod repos")
    parser.add_argument("--repos", default=str(DEFAULT_REPOS_JSON))
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--analysis-dir", default=str(DEFAULT_ANALYSIS_DIR))
    parser.add_argument("--top", type=int, default=50,
                        help="Analyze top N repos by relevance score (default: 50)")
    parser.add_argument("--skip-clone", action="store_true",
                        help="Skip cloning, only analyze already-cloned repos")
    parser.add_argument("--min-score", type=int, default=30,
                        help="Minimum relevance score to include (default: 30)")
    args = parser.parse_args()

    repos_path = Path(args.repos)
    if not repos_path.exists():
        print(f"ERROR: {repos_path} not found. Run scanner.py first.")
        sys.exit(1)

    with open(repos_path, encoding="utf-8") as f:
        data = json.load(f)

    repos = [r for r in data["repos"] if r["relevance_score"] >= args.min_score]
    repos = repos[:args.top]
    print(f"Analyzing {len(repos)} repos (top {args.top}, min score {args.min_score})")

    cache_dir = Path(args.cache_dir)
    analysis_dir = Path(args.analysis_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    per_repo_results = []

    for i, repo in enumerate(repos, 1):
        full_name = repo["full_name"]
        safe_name = full_name.replace("/", "__")
        repo_dir = cache_dir / safe_name
        repo_analysis_path = analysis_dir / f"{safe_name}.json"

        print(f"\n[{i}/{len(repos)}] {full_name} (score: {repo['relevance_score']}, *{repo['stars']})")

        if not args.skip_clone:
            if not repo_dir.exists():
                print(f"  Cloning {repo['html_url']} ...")
                ok = clone_or_update(repo["html_url"], repo_dir)
                if not ok:
                    print("  Skipping due to clone failure.")
                    continue
            else:
                print("  Already cloned.")
        elif not repo_dir.exists():
            print("  Not cloned yet — skipping (run without --skip-clone).")
            continue

        print("  Analyzing...")
        analysis = analyze_repo(repo_dir)
        print(f"  => {analysis['file_count']} Lua files, {len(analysis['callbacks'])} unique callbacks")

        result_entry = {
            "repo": full_name,
            "stars": repo["stars"],
            "relevance_score": repo["relevance_score"],
            "analysis": analysis,
        }
        per_repo_results.append(result_entry)

        with open(repo_analysis_path, "w", encoding="utf-8") as f:
            json.dump(result_entry, f, indent=2, ensure_ascii=False)

    # Build cross-repo index
    print("\n=== Building cross-repo index ===")
    index = merge_index(per_repo_results)
    index_path = analysis_dir / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Index saved to {index_path}")
    print(f"\nTop 30 callbacks by frequency:")
    for cb, count in list(index["callbacks_by_frequency"].items())[:30]:
        print(f"  {count:4d}x  {cb}")

    print(f"\nTop 20 API calls by frequency:")
    for call, count in list(index["api_calls_by_frequency"].items())[:20]:
        print(f"  {count:4d}x  {call}")


if __name__ == "__main__":
    main()
