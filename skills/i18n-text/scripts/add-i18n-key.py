"""
Add an i18n key to all language files atomically.

Inserts a new key into every language JSON file, maintaining alphabetical
sort order and valid JSON. Supports --dry-run for safe previewing.

Usage:
    python3 scripts/add-i18n-key.py --key KEY --en VALUE [OPTIONS]

Required:
    --key KEY        The i18n key to add (snake_case)
    --en VALUE       The English translation value

Options:
    --ar VALUE       Arabic translation
    --de VALUE       German translation
    --es VALUE       Spanish translation
    --fr VALUE       French translation
    --ru VALUE       Russian translation
    --tl VALUE       Tagalog translation
    --vi VALUE       Vietnamese translation
    --zh VALUE       Chinese (Simplified) translation
    --i18n-dir DIR   Path to the i18n directory (default: auto-detect)
    --dry-run        Preview changes without writing files
    --force          Overwrite existing key if present
    --help           Show this help message

Exit codes:
    0  Key added successfully to all files
    1  Key already exists (use --force to overwrite)
    2  Invalid arguments, missing files, or write error

Examples:
    python3 scripts/add-i18n-key.py --key "save_changes" --en "Save Changes"
    python3 scripts/add-i18n-key.py --key "hello" --en "Hello" --es "Hola" --fr "Bonjour" --dry-run
    python3 scripts/add-i18n-key.py --key "save" --en "Save" --force
"""

import argparse
import glob
import json
import os
import re
import sys

LANGUAGES = {
    "en": "English",
    "ar": "Arabic",
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "ru": "Russian",
    "tl": "Tagalog",
    "vi": "Vietnamese",
    "zh": "Chinese (Simplified)",
}


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
    sys.exit(2)


def validate_key(key: str) -> None:
    """Validate that the key follows snake_case convention."""
    if not re.match(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$', key):
        print(f"Error: Key '{key}' is not valid snake_case.", file=sys.stderr)
        print("Expected format: lowercase_with_underscores (e.g., 'save_changes')", file=sys.stderr)
        sys.exit(2)


def load_json_file(path: str) -> dict:
    """Load a JSON file preserving order."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(path: str, data: dict) -> None:
    """Write JSON with consistent formatting (2-space indent, trailing newline)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def insert_key_sorted(data: dict, key: str, value: str) -> dict:
    """Insert a key-value pair maintaining alphabetical sort order."""
    data[key] = value
    return dict(sorted(data.items()))


def main():
    parser = argparse.ArgumentParser(
        description="Add an i18n key to all language files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--key", required=True, help="The i18n key to add (snake_case)")
    parser.add_argument("--en", required=True, help="English translation value")
    parser.add_argument("--ar", help="Arabic translation")
    parser.add_argument("--de", help="German translation")
    parser.add_argument("--es", help="Spanish translation")
    parser.add_argument("--fr", help="French translation")
    parser.add_argument("--ru", help="Russian translation")
    parser.add_argument("--tl", help="Tagalog translation")
    parser.add_argument("--vi", help="Vietnamese translation")
    parser.add_argument("--zh", help="Chinese (Simplified) translation")
    parser.add_argument("--i18n-dir", help="Path to the i18n directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing key if present")
    args = parser.parse_args()

    validate_key(args.key)
    i18n_dir = find_i18n_dir(args.i18n_dir)
    print(f"Using i18n directory: {i18n_dir}", file=sys.stderr)

    # Build translations map
    translations = {}
    for lang in LANGUAGES:
        value = getattr(args, lang, None)
        if value:
            translations[lang] = value

    if "en" not in translations:
        print("Error: --en is required.", file=sys.stderr)
        sys.exit(2)

    # Check for existing key and process each file
    results = {}
    existing_in = []
    files_processed = {}

    for lang in LANGUAGES:
        path = os.path.join(i18n_dir, f"{lang}.i18n.json")
        if not os.path.isfile(path):
            results[lang] = {"status": "file_missing", "path": path}
            continue

        try:
            data = load_json_file(path)
        except (json.JSONDecodeError, OSError) as e:
            results[lang] = {"status": "error", "error": str(e)}
            continue

        if args.key in data and not args.force:
            existing_in.append(lang)
            results[lang] = {"status": "already_exists", "current_value": data[args.key]}
            continue

        value = translations.get(lang, translations["en"])
        new_data = insert_key_sorted(data, args.key, value)
        files_processed[lang] = (path, new_data)

        action = "would_add" if args.dry_run else "added"
        was_translated = lang in translations
        results[lang] = {
            "status": action,
            "value": value,
            "translated": was_translated,
            "needs_translation": not was_translated and lang != "en",
        }

    # If key exists and no --force, exit
    if existing_in and not args.force:
        output = {
            "key": args.key,
            "error": "key_already_exists",
            "exists_in": existing_in,
            "values": {lang: results[lang].get("current_value") for lang in existing_in},
            "hint": "Use --force to overwrite",
        }
        print(json.dumps(output, indent=2))
        sys.exit(1)

    # Write files (unless dry-run)
    if not args.dry_run:
        for lang, (path, new_data) in files_processed.items():
            try:
                write_json_file(path, new_data)
            except OSError as e:
                results[lang] = {"status": "write_error", "error": str(e)}

    needs_translation = [
        lang for lang, r in results.items()
        if r.get("needs_translation", False)
    ]

    output = {
        "key": args.key,
        "dry_run": args.dry_run,
        "results": results,
        "needs_translation": needs_translation,
        "summary": {
            "added": len([r for r in results.values() if r["status"] in ("added", "would_add")]),
            "already_existed": len(existing_in),
            "missing_files": len([r for r in results.values() if r["status"] == "file_missing"]),
            "errors": len([r for r in results.values() if r["status"] in ("error", "write_error")]),
        },
    }

    if needs_translation:
        output["translation_reminder"] = (
            f"The following languages received the English fallback and need proper translation: "
            f"{', '.join(needs_translation)}"
        )

    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
