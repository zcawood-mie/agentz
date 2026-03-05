"""
Find orphaned imports after code migration.

Given a source file path, finds all files that still import from it.
Helps verify that a migration is complete and the old file is safe to delete.

Usage:
    python3 scripts/find-orphaned-imports.py SOURCE_PATH [OPTIONS]

Arguments:
    SOURCE_PATH        The file path to check for remaining imports
                       (e.g., src/utils/emails.ts, services/old-module.js)

Options:
    --search-dirs DIRS   Comma-separated directories to search (default: src,test,lib,imports,client,server)
    --extensions EXTS    Comma-separated file extensions (default: ts,tsx,js,jsx,mjs)
    --check-exports      Also list exports from the source file
    --format FORMAT      Output format: json, text (default: json)
    --help               Show this help message

Exit codes:
    0  No remaining imports found — safe to delete
    1  Remaining imports found — migration incomplete
    2  Invalid arguments or source file not found

Examples:
    python3 scripts/find-orphaned-imports.py src/utils/emails.ts
    python3 scripts/find-orphaned-imports.py src/old-module.ts --check-exports
    python3 scripts/find-orphaned-imports.py lib/helpers.js --search-dirs src,test,lib --format text
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field


@dataclass
class ImportReference:
    file: str
    line: int
    import_statement: str
    import_type: str  # named, default, namespace, require, dynamic


@dataclass
class ExportInfo:
    name: str
    line: int
    export_type: str  # named, default, type, interface
    still_imported_by: list[str] = field(default_factory=list)


def find_files(search_dirs: list[str], extensions: list[str]) -> list[str]:
    """Recursively find all files matching the given extensions."""
    files = []
    ext_set = set(f".{e}" for e in extensions)

    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        for root, _, filenames in os.walk(search_dir):
            if any(skip in root for skip in ["node_modules", ".git", "dist", "build", ".meteor"]):
                continue
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if ext in ext_set:
                    files.append(os.path.join(root, filename))
    return files


def normalize_import_path(import_path: str, importing_file: str) -> str:
    """Resolve a relative import path to an absolute-ish path."""
    if import_path.startswith("."):
        base_dir = os.path.dirname(importing_file)
        resolved = os.path.normpath(os.path.join(base_dir, import_path))
        return resolved
    return import_path


def build_source_patterns(source_path: str) -> list[str]:
    """Build patterns to match imports of the source file."""
    base, _ = os.path.splitext(source_path)
    patterns = [source_path, base]
    basename = os.path.basename(base)
    patterns.append(basename)
    return patterns


def search_imports(files: list[str], source_path: str) -> list[ImportReference]:
    """Search files for imports of the source path."""
    references = []
    source_patterns = build_source_patterns(source_path)

    import_patterns = [
        (r'''import\s+.*?from\s+['"]([^'"]+)['"]''', "named"),
        (r'''import\s+['"]([^'"]+)['"]''', "side_effect"),
        (r'''import\s*\(\s*['"]([^'"]+)['"]''', "dynamic"),
        (r'''require\s*\(\s*['"]([^'"]+)['"]''', "require"),
        (r'''export\s+.*?from\s+['"]([^'"]+)['"]''', "reexport"),
    ]

    for file_path in files:
        if os.path.normpath(file_path) == os.path.normpath(source_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            continue

        for line_num, line in enumerate(lines, 1):
            for pattern, import_type in import_patterns:
                match = re.search(pattern, line)
                if not match:
                    continue

                import_path = match.group(1)
                resolved = normalize_import_path(import_path, file_path)

                for source_pattern in source_patterns:
                    normalized_source = os.path.normpath(source_pattern)
                    normalized_resolved = os.path.normpath(resolved)

                    if (normalized_resolved == normalized_source or
                            normalized_resolved.endswith(normalized_source) or
                            normalized_source.endswith(normalized_resolved)):
                        references.append(ImportReference(
                            file=file_path,
                            line=line_num,
                            import_statement=line.strip(),
                            import_type=import_type,
                        ))
                        break

    return references


def find_exports(source_path: str) -> list[ExportInfo]:
    """Find all exports in the source file."""
    if not os.path.isfile(source_path):
        return []

    exports = []
    try:
        with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except OSError:
        return []

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if re.match(r'^export\s+default\s+', stripped):
            name_match = re.search(r'export\s+default\s+(?:class|function|const|let|var)?\s*(\w+)', stripped)
            name = name_match.group(1) if name_match else "(default)"
            exports.append(ExportInfo(name=name, line=line_num, export_type="default"))
        elif re.match(r'^export\s+(?:const|let|var|function|class|async\s+function)\s+', stripped):
            name_match = re.search(r'export\s+(?:const|let|var|function|class|async\s+function)\s+(\w+)', stripped)
            if name_match:
                exports.append(ExportInfo(name=name_match.group(1), line=line_num, export_type="named"))
        elif re.match(r'^export\s+(?:type|interface)\s+', stripped):
            name_match = re.search(r'export\s+(?:type|interface)\s+(\w+)', stripped)
            if name_match:
                exports.append(ExportInfo(name=name_match.group(1), line=line_num, export_type="type"))
        elif re.match(r'^export\s*\{', stripped):
            names = re.findall(r'(\w+)(?:\s+as\s+\w+)?', stripped.replace('export', '', 1))
            for name in names:
                if name not in ('as', 'from', 'default'):
                    exports.append(ExportInfo(name=name, line=line_num, export_type="named"))

    return exports


def main():
    parser = argparse.ArgumentParser(
        description="Find files that still import from a migrated source file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes:\n  0  No imports remain\n  1  Imports still exist\n  2  Error",
    )
    parser.add_argument("source", help="Source file path to check for remaining imports")
    parser.add_argument("--search-dirs", default="src,test,lib,imports,client,server,tests",
                        help="Comma-separated directories to search")
    parser.add_argument("--extensions", default="ts,tsx,js,jsx,mjs",
                        help="Comma-separated file extensions")
    parser.add_argument("--check-exports", action="store_true",
                        help="Also list exports from the source file")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    args = parser.parse_args()

    source_path = args.source
    search_dirs = [d.strip() for d in args.search_dirs.split(",")]
    extensions = [e.strip().lstrip(".") for e in args.extensions.split(",")]

    print(f"Searching for imports of: {source_path}", file=sys.stderr)
    print(f"Search dirs: {', '.join(search_dirs)}", file=sys.stderr)

    all_files = find_files(search_dirs, extensions)
    print(f"Scanning {len(all_files)} files...", file=sys.stderr)

    references = search_imports(all_files, source_path)

    exports = []
    if args.check_exports:
        exports = find_exports(source_path)

    # Cross-reference exports with imports
    if exports and references:
        importing_files_content = {}
        for ref in references:
            if ref.file not in importing_files_content:
                try:
                    with open(ref.file, "r", encoding="utf-8", errors="ignore") as f:
                        importing_files_content[ref.file] = f.read()
                except OSError:
                    pass

        for export in exports:
            for ref in references:
                content = importing_files_content.get(ref.file, "")
                if export.name in content:
                    export.still_imported_by.append(ref.file)

    safe_to_delete = len(references) == 0

    if args.format == "json":
        output = {
            "source": source_path,
            "source_exists": os.path.isfile(source_path),
            "safe_to_delete": safe_to_delete,
            "import_count": len(references),
            "importing_files": sorted(set(r.file for r in references)),
            "references": [asdict(r) for r in references],
        }
        if args.check_exports:
            output["exports"] = [asdict(e) for e in exports]
            output["unused_exports"] = [e.name for e in exports if not e.still_imported_by]
        print(json.dumps(output, indent=2))
    else:
        print(f"Import analysis for: {source_path}")
        print(f"  Source exists: {os.path.isfile(source_path)}")
        print(f"  Safe to delete: {safe_to_delete}")
        print()

        if references:
            print(f"REMAINING IMPORTS ({len(references)}):")
            for ref in references:
                print(f"  {ref.file}:{ref.line} [{ref.import_type}]")
                print(f"    {ref.import_statement}")
        else:
            print("No remaining imports found.")

        if args.check_exports and exports:
            print()
            print(f"EXPORTS ({len(exports)}):")
            for exp in exports:
                status = "USED" if exp.still_imported_by else "UNUSED"
                print(f"  [{status}] {exp.name} ({exp.export_type}, line {exp.line})")
                if exp.still_imported_by:
                    for f in exp.still_imported_by:
                        print(f"    <- {f}")

    sys.exit(0 if safe_to_delete else 1)


if __name__ == "__main__":
    main()
