"""
Pre-push safety scanner.

Scans unpushed commits for secrets, debug artifacts, and other risky patterns.
Returns structured JSON so agents can parse results and decide whether to block.

Usage:
    python3 scripts/pre-push-scan.py [OPTIONS]

Options:
    --base REF       Base ref to diff against (default: auto-detect upstream)
    --format FORMAT  Output format: json, text (default: json)
    --help           Show this help message

Exit codes:
    0  No blocking issues found (warnings may exist)
    1  Blocking issues found — do NOT push
    2  Invalid arguments or git error

Examples:
    python3 scripts/pre-push-scan.py
    python3 scripts/pre-push-scan.py --base origin/main
    python3 scripts/pre-push-scan.py --format text
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Finding:
    severity: str  # "blocking" or "warning"
    category: str
    file: str
    line: int
    match: str
    context: str


# Blocking patterns — never push these
BLOCKING_PATTERNS = [
    (r'(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token)\s*[:=]\s*["\'][^"\']{8,}', "secret/key assignment"),
    (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][^"\']+["\']', "password assignment"),
    (r'(?i)private[_-]?key\s*[:=]', "private key assignment"),
    (r'(?i)connection[_-]?string\s*[:=]\s*["\']', "connection string"),
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "private key literal"),
    (r'(?i)(aws_secret|aws_access_key_id)\s*[:=]\s*["\']', "AWS credential"),
    (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}', "bearer token"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
    (r'sk-[a-zA-Z0-9]{32,}', "API secret key (OpenAI/Stripe style)"),
]

# Warning patterns — flag but don't block
WARNING_PATTERNS = [
    (r'console\.(log|debug|warn|error)\s*\(', "console statement"),
    (r'\bdebugger\b\s*;?', "debugger statement"),
    (r'(?i)\blocalhost\b', "localhost reference"),
    (r'127\.0\.0\.1', "loopback IP"),
    (r'/Users/[a-zA-Z]', "absolute macOS path"),
    (r'C:\\\\Users\\\\', "absolute Windows path"),
    (r'\.env\b(?!\.example|\.template|\.sample)', ".env file reference"),
    (r'TODO|FIXME|HACK|XXX', "TODO/FIXME marker"),
]


def get_base_ref(explicit_base: Optional[str]) -> str:
    """Determine the base ref to diff against."""
    if explicit_base:
        return explicit_base

    # Try upstream tracking branch
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "@{u}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        pass

    # Fall back to origin/main or origin/master
    for fallback in ["origin/main", "origin/master"]:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", fallback],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return fallback

    print("Error: Could not determine base ref. Use --base to specify.", file=sys.stderr)
    print("Usage: python3 scripts/pre-push-scan.py --base origin/main", file=sys.stderr)
    sys.exit(2)


def get_unpushed_diff(base_ref: str) -> str:
    """Get the diff of unpushed commits."""
    result = subprocess.run(
        ["git", "diff", f"{base_ref}..HEAD"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error: git diff failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return result.stdout


def get_unpushed_commits(base_ref: str) -> list[str]:
    """Get list of unpushed commit summaries."""
    result = subprocess.run(
        ["git", "log", "--oneline", f"{base_ref}..HEAD"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.strip().split("\n") if line]


def parse_diff_lines(diff_text: str) -> list[tuple[str, int, str]]:
    """Parse unified diff into (file, line_number, added_line) tuples."""
    results = []
    current_file = None
    current_line = 0

    for line in diff_text.split("\n"):
        if line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("@@ "):
            match = re.search(r'\+(\d+)', line)
            if match:
                current_line = int(match.group(1)) - 1
        elif line.startswith("+") and not line.startswith("+++"):
            current_line += 1
            if current_file:
                results.append((current_file, current_line, line[1:]))
        elif not line.startswith("-"):
            current_line += 1

    return results


def scan_diff(diff_text: str) -> list[Finding]:
    """Scan diff for blocking and warning patterns."""
    findings = []
    added_lines = parse_diff_lines(diff_text)

    for file_path, line_num, line_content in added_lines:
        # Skip binary files, lock files, and vendor directories
        if any(file_path.endswith(ext) for ext in [".lock", ".png", ".jpg", ".gif", ".ico", ".woff", ".woff2"]):
            continue
        if any(segment in file_path for segment in ["node_modules/", "vendor/", ".min.", "package-lock.json", "pnpm-lock.yaml"]):
            continue

        for pattern, category in BLOCKING_PATTERNS:
            match = re.search(pattern, line_content)
            if match:
                findings.append(Finding(
                    severity="blocking",
                    category=category,
                    file=file_path,
                    line=line_num,
                    match=match.group(0)[:80],
                    context=line_content.strip()[:120],
                ))

        for pattern, category in WARNING_PATTERNS:
            match = re.search(pattern, line_content)
            if match:
                findings.append(Finding(
                    severity="warning",
                    category=category,
                    file=file_path,
                    line=line_num,
                    match=match.group(0)[:80],
                    context=line_content.strip()[:120],
                ))

    return findings


def format_text(findings: list[Finding], commits: list[str]) -> str:
    """Format findings as human-readable text."""
    blocking = [f for f in findings if f.severity == "blocking"]
    warnings = [f for f in findings if f.severity == "warning"]

    lines = []
    lines.append(f"Pre-push scan: {len(commits)} unpushed commit(s)")
    lines.append("")

    if blocking:
        lines.append(f"BLOCKING ({len(blocking)} issue(s) — do NOT push):")
        for f in blocking:
            lines.append(f"  [{f.category}] {f.file}:{f.line}")
            lines.append(f"    {f.context}")
        lines.append("")

    if warnings:
        lines.append(f"WARNINGS ({len(warnings)} issue(s) — review before pushing):")
        for f in warnings:
            lines.append(f"  [{f.category}] {f.file}:{f.line}")
            lines.append(f"    {f.context}")
        lines.append("")

    if not blocking and not warnings:
        lines.append("No suspicious patterns found.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan unpushed commits for secrets, debug artifacts, and risky patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes:\n  0  No blocking issues\n  1  Blocking issues found\n  2  Invalid arguments or git error"
    )
    parser.add_argument("--base", help="Base ref to diff against (default: auto-detect upstream)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format (default: json)")
    args = parser.parse_args()

    base_ref = get_base_ref(args.base)
    print(f"Scanning diff against {base_ref}...", file=sys.stderr)

    diff_text = get_unpushed_diff(base_ref)
    if not diff_text.strip():
        print("No unpushed changes found.", file=sys.stderr)
        if args.format == "json":
            print(json.dumps({"base": base_ref, "commits": 0, "blocking": [], "warnings": []}, indent=2))
        else:
            print("No unpushed changes found.")
        sys.exit(0)

    commits = get_unpushed_commits(base_ref)
    findings = scan_diff(diff_text)

    blocking = [asdict(f) for f in findings if f.severity == "blocking"]
    warnings = [asdict(f) for f in findings if f.severity == "warning"]

    if args.format == "json":
        output = {
            "base": base_ref,
            "commits": len(commits),
            "has_blocking": len(blocking) > 0,
            "blocking": blocking,
            "warnings": warnings,
            "summary": {
                "blocking_count": len(blocking),
                "warning_count": len(warnings),
                "categories": list(set(f["category"] for f in blocking + warnings)),
            }
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text(findings, commits))

    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    main()
