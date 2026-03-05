"""
Check if an i18n key exists across all language files.

Searches the bluehive-i18n package for a given key and reports which
language files have it, which are missing it, and what values exist.

Usage:
    python3 scripts/check-i18n-key.py KEY [OPTIONS]

Arguments:
    KEY              The i18n key to search for (exact or substring)

Options:
    --exact          Exact key match only (default: substring search)
    --i18n-dir DIR   Path to the i18n directory (default: auto-detect)
    --format FORMAT  Output format: json, text (default: json)
    --help           Show this help message

Exit codes:
    0  Key found in all language files
    1  Key missing from one or more files
    2  Key not found in any file, or invalid arguments

Examples:
    python3 scripts/check-i18n-key.py save_changes
    python3 scripts/check-i18n-key.py save_changes --exact
    python3 scripts/check-i18n-key.py "no_results" --format text
"""

import argparse
import glob
import json
import os
import sys

EXPECTED_LANGUAGES = ["en", "ar", "de", "es", "fr", "ru", "tl", "vi", "zh"]


def find_i18n_dir(explicit_dir: str | None) -> str:
    """Locate the i18n directory by searching common paths."""
    if explicit_dir:
        if os.path.isdir(explicit_dir):
            return explicit_dir
        print(f"Error: Directory not found: {explicit_dir}", file=sys.stderr)
        sys.exit(2)

    search_paths = [
        "packages/bluehive-i18n/i18n",
        "../packages/bluehive-i18n/i18n",
        "../../packages/bluehive-i18n/i18n",
    ]

    home = os.path.expanduser("~")
    workspace_globs = [
        f"{home}/bhDev/worktrees/*/packages/bluehive-i18n/i18n",
        f"{home}/bhDev/masterRepos/*/packages/bluehive-i18n/i18n",
    ]

    for path in search_paths:
        if os.path.isdir(path):
            return path

    for pattern in workspace_globs:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    print("Error: Could not find i18n directory. Use --i18n-dir to specify.", file=sys.stderr)
    print("Expected: packages/bluehive-i18n/i18n/", file=sys.stderr)
    sys.exit(2)


def load_language_file(i18n_dir: str, lang: str) -> dict | None:
    """Load a language JSON file, return None if not found."""
    path = os.path.join(i18n_dir, f"{lang}.i18n.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not parse {path}: {e}", file=sys.stderr)
        return None


def search_key(data: dict, key: str, exact: bool) -> list[tuple[str, str]]:
    """Search for key in flat JSON dict. Returns list of (key, value) matches."""
    matches = []
    for k, v in data.items():
        if exact and k == key:
            matches.append((k, str(v)))
        elif not exact and key.lower() in k.lower():
            matches.append((k, str(v)))
    return matches


def main():
    parser = argparse.ArgumentParser(
        description="Check if an i18n key exists across all language files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes:\n  0  Key found in all files\n  1  Key missing from some files\n  2  Key not found anywhere",
    )
    parser.add_argument("key", help="The i18n key to search for")
    parser.add_argument("--exact", action="store_true", help="Exact key match only (default: substring)")
    parser.add_argument("--i18n-dir", help="Path to the i18n directory")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format (default: json)")
    args = parser.parse_args()

    i18n_dir = find_i18n_dir(args.i18n_dir)
    print(f"Searching in: {i18n_dir}", file=sys.stderr)

    results = {}
    all_matched_keys = set()

    for lang in EXPECTED_LANGUAGES:
        data = load_language_file(i18n_dir, lang)
        if data is None:
            results[lang] = {"status": "file_missing", "matches": []}
            continue

        matches = search_key(data, args.key, args.exact)
        all_matched_keys.update(k for k, _ in matches)

        if matches:
            results[lang] = {
                "status": "found",
                "matches": [{"key": k, "value": v} for k, v in matches],
            }
        else:
            results[lang] = {"status": "missing", "matches": []}

    found_langs = [l for l, r in results.items() if r["status"] == "found"]
    missing_langs = [l for l, r in results.items() if r["status"] == "missing"]
    missing_files = [l for l, r in results.items() if r["status"] == "file_missing"]

    if args.format == "json":
        output = {
            "query": args.key,
            "exact": args.exact,
            "i18n_dir": i18n_dir,
            "matched_keys": sorted(all_matched_keys),
            "found_in": found_langs,
            "missing_from": missing_langs,
            "file_missing": missing_files,
            "complete": len(missing_langs) == 0 and len(missing_files) == 0 and len(found_langs) > 0,
            "languages": results,
        }
        print(json.dumps(output, indent=2))
    else:
        mode = "exact" if args.exact else "substring"
        print(f"Search for '{args.key}' ({mode} match):")
        print(f"  Matched keys: {', '.join(sorted(all_matched_keys)) or '(none)'}")
        print(f"  Found in: {', '.join(found_langs) or '(none)'}")
        if missing_langs:
            print(f"  MISSING from: {', '.join(missing_langs)}")
        if missing_files:
            print(f"  File missing: {', '.join(missing_files)}")
        print()
        if found_langs:
            print("Values:")
            for lang in found_langs:
                for m in results[lang]["matches"]:
                    print(f"  [{lang}] {m['key']} = {m['value']}")

    if not all_matched_keys:
        sys.exit(2)
    elif missing_langs or missing_files:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
