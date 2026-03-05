"""
Analyze a git diff to categorize changes and flag diff bloat.

Parses the diff between two refs and categorizes each changed file as
substantive, whitespace-only, moved, or trivial. Helps identify
unnecessary changes that inflate PR size.

Usage:
    python3 scripts/analyze-diff.py [OPTIONS]

Options:
    --base REF         Base ref to diff against (default: auto-detect upstream)
    --head REF         Head ref (default: HEAD)
    --format FORMAT    Output format: json, text (default: json)
    --threshold N      Flag files with more than N whitespace-only changes (default: 5)
    --help             Show this help message

Exit codes:
    0  Analysis complete, no bloat detected
    1  Analysis complete, bloat detected (files flagged)
    2  Invalid arguments or git error

Examples:
    python3 scripts/analyze-diff.py
    python3 scripts/analyze-diff.py --base origin/master
    python3 scripts/analyze-diff.py --format text
    python3 scripts/analyze-diff.py --base main --threshold 3
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict, field


@dataclass
class FileAnalysis:
    file: str
    status: str  # added, modified, deleted, renamed
    lines_added: int = 0
    lines_removed: int = 0
    category: str = ""  # substantive, whitespace_only, import_reorder, trivial
    whitespace_only_changes: int = 0
    import_changes: int = 0
    blank_line_changes: int = 0
    substantive_changes: int = 0
    flags: list[str] = field(default_factory=list)


def get_base_ref(explicit_base: str | None) -> str:
    """Determine the base ref to diff against."""
    if explicit_base:
        return explicit_base

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "@{u}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        pass

    for fallback in ["origin/main", "origin/master"]:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", fallback],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return fallback

    print("Error: Could not determine base ref. Use --base to specify.", file=sys.stderr)
    sys.exit(2)


def get_merge_base(base_ref: str, head_ref: str) -> str:
    """Find the merge base between two refs."""
    result = subprocess.run(
        ["git", "merge-base", base_ref, head_ref],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return base_ref
    return result.stdout.strip()


def get_diff_stat(merge_base: str, head_ref: str) -> list[dict]:
    """Get diff --numstat for line counts."""
    result = subprocess.run(
        ["git", "diff", "--numstat", f"{merge_base}..{head_ref}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error: git diff failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(2)

    files = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            added = int(parts[0]) if parts[0] != "-" else 0
            removed = int(parts[1]) if parts[1] != "-" else 0
            files.append({"file": parts[2], "added": added, "removed": removed})
    return files


def get_diff_name_status(merge_base: str, head_ref: str) -> dict[str, str]:
    """Get file status (added, modified, deleted, renamed)."""
    result = subprocess.run(
        ["git", "diff", "--name-status", f"{merge_base}..{head_ref}"],
        capture_output=True, text=True
    )
    statuses = {}
    status_map = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed"}
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        status_char = parts[0][0]
        file_name = parts[-1]
        statuses[file_name] = status_map.get(status_char, "unknown")
    return statuses


def get_full_diff(merge_base: str, head_ref: str) -> str:
    """Get the full unified diff."""
    result = subprocess.run(
        ["git", "diff", f"{merge_base}..{head_ref}"],
        capture_output=True, text=True
    )
    return result.stdout


def classify_line(line: str) -> str:
    """Classify a diff line as whitespace, import, blank, or substantive."""
    content = line[1:] if line and line[0] in ('+', '-') else line

    if content.strip() == "":
        return "blank"

    stripped = content.strip()

    if re.match(r'^(import\s|from\s|const\s+\w+\s*=\s*require|export\s+(default\s+)?{)', stripped):
        return "import"

    return "substantive"


def analyze_file_diff(file_path: str, diff_text: str) -> dict:
    """Analyze the diff for a single file."""
    whitespace = 0
    imports = 0
    blanks = 0
    substantive = 0

    in_file = False
    for line in diff_text.split("\n"):
        if line.startswith("+++ b/"):
            current_file = line[6:]
            in_file = current_file == file_path
            continue
        if line.startswith("--- "):
            continue
        if line.startswith("diff --git"):
            if in_file:
                break
            continue

        if not in_file:
            continue

        if line.startswith("@@"):
            continue

        if line.startswith("+") or line.startswith("-"):
            category = classify_line(line)
            if category == "blank":
                blanks += 1
            elif category == "import":
                imports += 1
            elif category == "substantive":
                substantive += 1
            else:
                whitespace += 1

    return {
        "whitespace": whitespace,
        "imports": imports,
        "blanks": blanks,
        "substantive": substantive,
    }


def categorize_file(analysis: FileAnalysis) -> str:
    """Determine overall category for a file."""
    if analysis.substantive_changes == 0:
        if analysis.import_changes > 0 and analysis.whitespace_only_changes == 0:
            return "import_reorder"
        if analysis.blank_line_changes + analysis.whitespace_only_changes > 0:
            return "whitespace_only"
        return "trivial"
    return "substantive"


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a git diff to categorize changes and flag bloat.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes:\n  0  No bloat\n  1  Bloat detected\n  2  Error",
    )
    parser.add_argument("--base", help="Base ref to diff against (default: auto-detect)")
    parser.add_argument("--head", default="HEAD", help="Head ref (default: HEAD)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--threshold", type=int, default=5, help="Whitespace change threshold for flagging")
    args = parser.parse_args()

    base_ref = get_base_ref(args.base)
    merge_base = get_merge_base(base_ref, args.head)
    print(f"Analyzing diff: {merge_base[:8]}..{args.head}", file=sys.stderr)

    stat = get_diff_stat(merge_base, args.head)
    statuses = get_diff_name_status(merge_base, args.head)
    full_diff = get_full_diff(merge_base, args.head)

    if not stat:
        print("No changes found.", file=sys.stderr)
        output = {"base": base_ref, "merge_base": merge_base, "head": args.head, "files": [], "bloat_detected": False}
        print(json.dumps(output, indent=2))
        sys.exit(0)

    analyses = []
    for file_info in stat:
        file_path = file_info["file"]
        line_analysis = analyze_file_diff(file_path, full_diff)

        fa = FileAnalysis(
            file=file_path,
            status=statuses.get(file_path, "modified"),
            lines_added=file_info["added"],
            lines_removed=file_info["removed"],
            whitespace_only_changes=line_analysis["whitespace"],
            import_changes=line_analysis["imports"],
            blank_line_changes=line_analysis["blanks"],
            substantive_changes=line_analysis["substantive"],
        )

        fa.category = categorize_file(fa)

        if fa.category == "whitespace_only":
            fa.flags.append("whitespace_only_file")
        if fa.category == "import_reorder":
            fa.flags.append("import_reorder_only")
        if fa.blank_line_changes > args.threshold and fa.substantive_changes < fa.blank_line_changes:
            fa.flags.append("excessive_blank_line_changes")

        analyses.append(fa)

    flagged = [a for a in analyses if a.flags]
    bloat_detected = len(flagged) > 0
    total_added = sum(a.lines_added for a in analyses)
    total_removed = sum(a.lines_removed for a in analyses)

    categories = {}
    for a in analyses:
        categories.setdefault(a.category, []).append(a.file)

    if args.format == "json":
        output = {
            "base": base_ref,
            "merge_base": merge_base,
            "head": args.head,
            "bloat_detected": bloat_detected,
            "summary": {
                "total_files": len(analyses),
                "total_added": total_added,
                "total_removed": total_removed,
                "substantive_files": len(categories.get("substantive", [])),
                "whitespace_only_files": len(categories.get("whitespace_only", [])),
                "import_reorder_files": len(categories.get("import_reorder", [])),
                "trivial_files": len(categories.get("trivial", [])),
                "flagged_files": len(flagged),
            },
            "flagged": [asdict(a) for a in flagged],
            "files": [asdict(a) for a in analyses],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Diff analysis: {merge_base[:8]}..{args.head}")
        print(f"  Total files: {len(analyses)}  (+{total_added} -{total_removed})")
        print(f"  Substantive: {len(categories.get('substantive', []))}")
        print(f"  Whitespace only: {len(categories.get('whitespace_only', []))}")
        print(f"  Import reorder: {len(categories.get('import_reorder', []))}")
        print(f"  Trivial: {len(categories.get('trivial', []))}")
        print()

        if flagged:
            print(f"BLOAT DETECTED ({len(flagged)} file(s) flagged):")
            for a in flagged:
                flags_str = ", ".join(a.flags)
                print(f"  {a.file} [{flags_str}]")
                print(f"    +{a.lines_added} -{a.lines_removed} "
                      f"(substantive: {a.substantive_changes}, ws: {a.whitespace_only_changes}, "
                      f"blank: {a.blank_line_changes}, import: {a.import_changes})")
            print()
            print("Consider reverting whitespace-only and import-reorder changes to minimize diff.")
        else:
            print("No bloat detected. All changes appear substantive.")

    sys.exit(1 if bloat_detected else 0)


if __name__ == "__main__":
    main()
