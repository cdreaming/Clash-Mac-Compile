#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = [
    re.compile(r"\bUndefined symbols for architecture\b", re.I),
    re.compile(r"\bduplicate symbol\b", re.I),
    re.compile(r"\bframework not found\b", re.I),
    re.compile(r"\blibrary not found\b", re.I),
    re.compile(r"\bfile not found\b", re.I),
    re.compile(r"\bsymbol\(s\) not found\b", re.I),
    re.compile(r"\blink(er)? command failed\b", re.I),
    re.compile(r"^\s*ld:\s", re.I),
    re.compile(r"^\s*clang:\s+error:", re.I),
    re.compile(r"^\s*error:\s", re.I),
]

def main() -> int:
    parser = argparse.ArgumentParser(description="Extract linker/build errors from a verbose Xcode log.")
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--context-lines", type=int, default=3)
    args = parser.parse_args()

    if args.context_lines < 0 or args.context_lines > 20:
        parser.error("--context-lines must be between 0 and 20")
    lines = args.log.read_text(encoding="utf-8", errors="replace").splitlines()
    matches = [i for i, line in enumerate(lines) if any(p.search(line) for p in PATTERNS)]
    selected = set()
    for index in matches:
        start = max(0, index - args.context_lines)
        end = min(len(lines), index + args.context_lines + 1)
        selected.update(range(start, end))

    output = [
        "# Xcode Build / Linker Diagnostics",
        "",
        f"- Source log: `{args.log.name}`",
        f"- Total log lines: {len(lines)}",
        f"- Matched diagnostic lines: {len(matches)}",
        "",
    ]
    if not matches:
        output.extend([
            "No standard linker error signature was detected automatically.",
            "Inspect the complete `XCODEBUILD.log`; Xcode may report a target-specific failure without a conventional `ld:` prefix.",
        ])
    else:
        output.append("```text")
        previous = -2
        for index in sorted(selected):
            if index > previous + 1:
                output.append("...")
            output.append(f"{index + 1}: {lines[index]}")
            previous = index
        output.append("```")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Linker diagnostics: {len(matches)} matching lines from {len(lines)} log lines")
    print(f"Report: {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
